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

