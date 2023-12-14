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
