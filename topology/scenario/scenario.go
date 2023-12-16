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
