# Changelog

All notable changes to Federift are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); this project uses simple
semantic-ish versions.

## [0.5.0] - 2026-09-01

### Added
- Go topology engine (`topology/`): per-round latency, drops, stragglers, and
  scheduled partitions, all deterministic from the scenario seed.
- `-emit-trace` on the Go CLI producing a compact reachability document.
- Python `run --trace` consumes the Go trace, dropping unreachable clients from
  the round - the first end-to-end coupling of the two halves.
- Two animated SVGs (topology + privacy/convergence) under `docs/assets/`.

### Changed
- Scenario schema formalised into three namespaced blocks (`federation`,
