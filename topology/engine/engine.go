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
