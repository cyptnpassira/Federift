// Command topology is the federift network topology engine.
//
// It reads a shared scenario JSON, simulates per-round network behaviour
// (latency, drops, stragglers, partitions), and either prints a human report
// or emits a compact reachability trace that the Python privacy core consumes
// via `federift run --trace`.
//
// Usage:
//
//	topology -scenario path.json                 # text report
//	topology -scenario path.json -emit-trace out.json
//	topology -scenario path.json -json           # full JSON round results
//
// stdlib only.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/cyptnpassira/Federift/topology/engine"
	"github.com/cyptnpassira/Federift/topology/scenario"
)

func main() {
	scPath := flag.String("scenario", "", "path to shared scenario JSON (required)")
	emitTrace := flag.String("emit-trace", "", "write reachability trace JSON to this path")
	asJSON := flag.Bool("json", false, "print full round results as JSON")
	flag.Parse()

