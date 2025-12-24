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
