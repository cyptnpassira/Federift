# Examples

Runnable end-to-end demos coupling the Go network engine to the Python privacy
core.

## `pipeline.sh` / `pipeline.ps1`

Both do the same two steps:

1. Run the Go topology engine with `-emit-trace` to produce `trace.json`.
2. Run `python -m federift run <scenario> --trace trace.json`, so the Python
   round drops exactly the clients the network made unreachable.

