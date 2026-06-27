# Examples

Runnable end-to-end demos coupling the Go network engine to the Python privacy
core.

## `pipeline.sh` / `pipeline.ps1`

Both do the same two steps:

1. Run the Go topology engine with `-emit-trace` to produce `trace.json`.
2. Run `python -m federift run <scenario> --trace trace.json`, so the Python
   round drops exactly the clients the network made unreachable.

```bash
# POSIX
./examples/pipeline.sh                                   # fractured-robust
./examples/pipeline.sh federift/scenarios/noniid-dp.json # any scenario
```

```powershell
# Windows PowerShell
./examples/pipeline.ps1
./examples/pipeline.ps1 -Scenario federift/scenarios/noniid-dp.json
```

## What to look for

- The Python **drop** column spikes during the partition windows defined in the
  scenario's `network.partitions`.
- **convergence** flattens while a cluster is isolated and resumes after.
- With `sigma > 0`, the privacy block prints approximate ε and the leakage
  signals shrink relative to the `sigma = 0` baseline.

Nothing here is a benchmark — it's a teaching loop. See the README's honesty
section before drawing conclusions.

# draft note 9
