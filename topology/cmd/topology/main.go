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
