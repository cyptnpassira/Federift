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

	if *scPath == "" {
		fmt.Fprintln(os.Stderr, "error: -scenario is required")
		flag.Usage()
		os.Exit(2)
	}

	sc, err := scenario.Load(*scPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	rounds := engine.Run(sc)

	if *emitTrace != "" {
		trace := engine.BuildTrace(sc.Name, rounds)
		if err := writeJSON(*emitTrace, trace); err != nil {
			fmt.Fprintf(os.Stderr, "error writing trace: %v\n", err)
			os.Exit(1)
		}
		fmt.Fprintf(os.Stderr, "wrote trace for %d rounds -> %s\n", len(rounds), *emitTrace)
	}

	if *asJSON {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		_ = enc.Encode(rounds)
		return
	}

	printReport(sc, rounds)
}

func writeJSON(path string, v interface{}) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	return enc.Encode(v)
}

