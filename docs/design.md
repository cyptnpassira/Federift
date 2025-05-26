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

