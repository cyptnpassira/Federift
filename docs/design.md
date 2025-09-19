# Design notes

This document explains *why* federift is shaped the way it is. For usage, see
the top-level README.

## Two languages, one file

The hard constraint driving the whole design: **Python and Go must never share
code, only a file.** That forces a clean contract — the scenario JSON — and
makes each half independently runnable and independently teachable.

- Python owns the *math you'd write in a notebook*: aggregation, noise,
  privacy accounting, leakage signals.
- Go owns the *systems layer you'd write in a service*: latency, packet loss,
  stragglers, network partitions.

They meet through `-emit-trace` → `run --trace`. Go decides who is reachable;
Python decides what that reachability does to learning and privacy.

## Why toy vectors instead of a real model

A real model would drown the systems/privacy lesson in optimizer and dataset
detail. Instead, each client owns a fixed target vector derived from its label
distribution, and "training" is a deterministic pull toward it. This keeps:

- **determinism** — every run reproduces, so a change in a report is caused by
  a change in *the thing you edited*, not RNG noise;
- **legibility** — convergence is literally "distance to target", and the
  effect of non-IID skew or DP noise is visible in a handful of rounds.

The cost is honesty: these clients don't learn anything real, and the README
says so loudly.

## The RNG discipline

All randomness flows from one master seed through
`sha256(master :: label-parts)` sub-streams (`rng.py` in Python, an FNV-based
mirror in Go). Two consequences:

1. Independent effects (client selection, jitter, drops) never accidentally
   correlate through a shared stream.
2. Any single draw can be reproduced in isolation for debugging.

## Privacy accounting: deliberately approximate

federift uses the closed-form Gaussian-mechanism bound and both composition
theorems. This is a **teaching seam**, isolated in `privacy.account`, so that
the natural next exercise — "replace this with a real RDP accountant" — touches
exactly one function. The README's honesty section exists precisely because
these bounds are loose and must not be mistaken for guarantees.

## Extensibility rule of thumb

If a change forces *both* languages to recompile together, it's modelled wrong.
Add fields under the block owned by one side; the other side ignores unknown
JSON keys by construction.

## Determinism note

Both halves are seeded from the same scenario seed, and the Python RNG
fan-out is stable across runs on the same interpreter. The Go engine takes
its own seed from the same field. If you change the partitioning or the
aggregation order, the numeric output changes: keep the seed field in the
scenario file when you want a reproducible report.
