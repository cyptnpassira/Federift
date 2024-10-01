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
  `privacy`, `network`) so each language ignores what it doesn't own.

## [0.4.0] - 2026-08-24

### Added
- Approximate DP accounting: Gaussian-mechanism plus naive **and** advanced
  composition; reports the tighter of the two.
- Leakage heuristics module (`leakage.py`): update distinguishability and
  gradient-cosine leak, surfaced in the CLI report.
- `privacy` subcommand for accounting-only output.

### Changed
- Server-side Gaussian noise wired into the round loop; `sigma = 0` documented
  as the explicit non-private baseline.

## [0.3.0] - 2025-11-18

### Added
- Aggregation rules beyond FedAvg: uniform mean, coordinate-wise trimmed mean,
  and a simplified multi-Krum selection.
- Dirichlet non-IID partitioner with a stdlib-only gamma sampler.
- `partition` subcommand with a per-client skew-index report.

## [0.2.0] - 2024-06-21

### Added
