// Package scenario parses the shared JSON scenario file. Only the fields the
// Go topology engine cares about (the "network" block plus a little federation
// metadata) are decoded; everything else is ignored, keeping the Go and Python
// tools loosely coupled around one file.
package scenario

import (
	"encoding/json"
	"fmt"
	"os"
)

// Partition describes a network split isolating a set of clients over a
// contiguous range of rounds [RoundStart, RoundEnd).
type Partition struct {
	RoundStart int   `json:"round_start"`
	RoundEnd   int   `json:"round_end"`
	Isolated   []int `json:"isolated"`
}

// Network holds all topology-engine parameters.
type Network struct {
	BaseLatencyMs    float64     `json:"base_latency_ms"`
	JitterMs         float64     `json:"jitter_ms"`
	DropProb         float64     `json:"drop_prob"`
	StragglerProb    float64     `json:"straggler_prob"`
	StragglerExtraMs float64     `json:"straggler_extra_ms"`
	DeadlineMs       float64     `json:"deadline_ms"`
	Partitions       []Partition `json:"partitions"`
}

// Federation carries just enough shape for the engine to know how many
// clients/rounds to simulate. The privacy fields live here too but are unused
// on the Go side.
type Federation struct {
	NumClients     int `json:"num_clients"`
	Rounds         int `json:"rounds"`
	ClientsPerRound int `json:"clients_per_round"`
}

// Scenario is the top-level shared document.
type Scenario struct {
	Name       string     `json:"name"`
	Seed       int64      `json:"seed"`
	Federation Federation `json:"federation"`
	Network    Network    `json:"network"`
}

// Defaults fills sensible values for anything left at zero.
func (s *Scenario) Defaults() {
	if s.Federation.NumClients == 0 {
		s.Federation.NumClients = 10
	}
	if s.Federation.Rounds == 0 {
		s.Federation.Rounds = 20
	}
	if s.Federation.ClientsPerRound == 0 {
		s.Federation.ClientsPerRound = s.Federation.NumClients
	}
