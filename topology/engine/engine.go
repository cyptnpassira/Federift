// Package engine simulates a federated round's network behaviour: per-client
// latency, random drops, straggler tails, and scheduled partitions. It is a
// deterministic discrete simulation seeded from the scenario, so runs are
// reproducible and can be diffed against the Python privacy core.
package engine

import (
	"hash/fnv"
	"math"
	"math/rand"
	"sort"

	"github.com/cyptnpassira/Federift/topology/scenario"
)

// ClientResult is the outcome for one client in one round.
type ClientResult struct {
	Client    int     `json:"client"`
	LatencyMs float64 `json:"latency_ms"`
	Dropped   bool    `json:"dropped"`
	Straggler bool    `json:"straggler"`
	Isolated  bool    `json:"isolated"`
	Reachable bool    `json:"reachable"`
}

// RoundResult aggregates a round.
type RoundResult struct {
	Round     int            `json:"round"`
	Selected  []int          `json:"selected"`
	Reachable []int          `json:"reachable"`
	Clients   []ClientResult `json:"clients"`
	P50Ms     float64        `json:"p50_ms"`
	P95Ms     float64        `json:"p95_ms"`
	DropRate  float64        `json:"drop_rate"`
}

// Trace is the compact per-round reachability document consumed by the Python
// simulator via `federift run --trace`.
type TraceRound struct {
	Round     int   `json:"round"`
	Reachable []int `json:"reachable"`
}

type Trace struct {
	Scenario string       `json:"scenario"`
	Rounds   []TraceRound `json:"rounds"`
}

// subSeed derives a stable per-(round,client,label) seed so each stochastic
// draw is independent yet reproducible.
func subSeed(master int64, round, client int, label string) int64 {
	h := fnv.New64a()
	var buf [24]byte
	putI64(buf[0:8], master)
	putI64(buf[8:16], int64(round)<<20|int64(client))
	_, _ = h.Write(buf[:16])
	_, _ = h.Write([]byte(label))
	return int64(h.Sum64() & 0x7FFFFFFFFFFFFFFF)
}

func putI64(b []byte, v int64) {
	for i := 0; i < 8; i++ {
		b[i] = byte(v >> (8 * i))
	}
}

func isolatedSet(net scenario.Network, round int) map[int]bool {
	set := map[int]bool{}
	for _, p := range net.Partitions {
		if round >= p.RoundStart && round < p.RoundEnd {
			for _, c := range p.Isolated {
				set[c] = true
			}
		}
	}
	return set
}

// selectClients picks the round's participant set deterministically. It mirrors
// the intent of the Python selector (a seeded sample) but the Go engine only
// needs the set, not identical membership, since Python re-selects and then
// intersects with the trace's reachable set.
func selectClients(master int64, round, n, k int) []int {
	if k >= n {
		out := make([]int, n)
		for i := range out {
			out[i] = i
		}
		return out
	}
	r := rand.New(rand.NewSource(subSeed(master, round, -1, "select")))
	perm := r.Perm(n)[:k]
	sort.Ints(perm)
	return perm
}

// RunRound simulates a single round.
func RunRound(sc *scenario.Scenario, round int) RoundResult {
	net := sc.Network
	iso := isolatedSet(net, round)
	selected := selectClients(sc.Seed, round, sc.Federation.NumClients, sc.Federation.ClientsPerRound)

	res := RoundResult{Round: round, Selected: selected}
	var latencies []float64
	dropped := 0

	for _, c := range selected {
		cr := ClientResult{Client: c}

		if iso[c] {
			cr.Isolated = true
			cr.Dropped = true
			cr.Reachable = false
			res.Clients = append(res.Clients, cr)
			dropped++
			continue
		}

		rDrop := rand.New(rand.NewSource(subSeed(sc.Seed, round, c, "drop")))
		if rDrop.Float64() < net.DropProb {
			cr.Dropped = true
			cr.Reachable = false
			res.Clients = append(res.Clients, cr)
			dropped++
			continue
		}

		rLat := rand.New(rand.NewSource(subSeed(sc.Seed, round, c, "lat")))
		lat := net.BaseLatencyMs + (rLat.Float64()*2-1)*net.JitterMs
		if lat < 0 {
			lat = 0
		}

		rStr := rand.New(rand.NewSource(subSeed(sc.Seed, round, c, "straggle")))
		if rStr.Float64() < net.StragglerProb {
			cr.Straggler = true
			lat += net.StragglerExtraMs
		}

		cr.LatencyMs = lat
		// A client past the deadline is effectively dropped from aggregation.
		if lat > net.DeadlineMs {
			cr.Dropped = true
			cr.Reachable = false
			dropped++
		} else {
			cr.Reachable = true
			latencies = append(latencies, lat)
			res.Reachable = append(res.Reachable, c)
		}
		res.Clients = append(res.Clients, cr)
	}

	res.P50Ms = percentile(latencies, 0.50)
	res.P95Ms = percentile(latencies, 0.95)
	if len(selected) > 0 {
		res.DropRate = float64(dropped) / float64(len(selected))
	}
	sort.Ints(res.Reachable)
	return res
}

// Run simulates every round of the scenario.
func Run(sc *scenario.Scenario) []RoundResult {
	out := make([]RoundResult, 0, sc.Federation.Rounds)
	for r := 0; r < sc.Federation.Rounds; r++ {
		out = append(out, RunRound(sc, r))
	}
	return out
}

// BuildTrace converts full round results into the compact reachability trace.
