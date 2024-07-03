# Changelog

All notable changes to Federift are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); this project uses simple
semantic-ish versions.

## [0.5.0] - 2026-09-01

### Added
- Go topology engine (`topology/`): per-round latency, drops, stragglers, and
  scheduled partitions, all deterministic from the scenario seed.
- `-emit-trace` on the Go CLI producing a compact reachability document.
