<div align="center">

# Federift

a small federated-learning network and privacy simulator that fractures on cue

<sub>Python stdlib privacy core · Go stdlib topology engine · one shared JSON scenario</sub>

<img src="docs/assets/topology.svg" alt="A federated aggregator ringed by client nodes; a left cluster is periodically isolated by a partition while the right cluster keeps contributing" width="640" />

</div>

> Read this first. Federift is an educational systems simulation. It is not a
> privacy proof, not a real ML training system, and its differential-privacy
> numbers are loose closed-form approximations. Do not use any output here to
> make a claim about the privacy of a real system. The full disclaimer is in
> [The honest part](#the-honest-part-read-twice).

## The one-sentence version

Federift splits a toy federated round across two languages that never import
each other, and makes them meet at exactly one place: a JSON scenario file.
Python runs the learning and privacy math; Go runs the network. Go can hand
Python a reachability trace so the privacy core sees the same drops and
partitions the network produced.

## Why break the network on purpose

Federated learning is usually drawn as a tidy star: a server, some clients, a
few arrows. Reality is a network that drops packets, stalls on stragglers, and
splits into islands. Federift makes the breakage first-class:

- **latency**: per-client base plus jitter, deterministic per (round, client).
- **drops**: Bernoulli packet loss before an update ever leaves.
- **stragglers**: a heavy tail that pushes a client past the round deadline.
- **partitions**: scheduled windows where a named set of clients is isolated
  from the aggregator entirely.

Each of those removes a client from a round. That changes who contributes,
which changes what the aggregate reveals, which is where the privacy story
starts. The whole repository exists to let you watch those three things move
together.

## The two halves

### Python, the privacy core (`federift/`)

Pure standard library. No numpy, no torch. Vectors are `list[float]`.

| module | responsibility |
|---|---|
| `vectors.py`   | vector math (`add`, `mean`, `clip_l2`, `l2_distance`) |
| `rng.py`       | seed fan-out via SHA-256 into reproducible sub-streams |
| `partition.py` | IID split plus Dirichlet(alpha) non-IID label skew |
| `clients.py`   | deterministic toy-vector clients, each with a target from its label mix |
| `aggregate.py` | FedAvg, uniform mean, coordinate-wise trimmed mean, simplified multi-Krum |
| `privacy.py`   | Gaussian-mechanism noise plus approximate (epsilon, delta) accounting |
| `leakage.py`   | membership and leakage heuristics (distinguishability, gradient cosine) |
| `simulator.py` | the round loop that ties it together and can consume a Go trace |
| `cli.py`       | text and JSON reports |

### Go, the topology engine (`topology/`)

Also pure standard library (`math/rand`, `hash/fnv`, `encoding/json`).

| package | responsibility |
|---|---|
| `scenario/` | parses the shared JSON (only the fields Go needs) |
| `engine/`   | per-round latency, drop, straggler, and partition simulation |
| `cmd/topology/` | CLI: text report, full JSON, or `-emit-trace` for Python |

The two sides are decoupled: each ignores JSON fields it does not understand,
so you can extend one without recompiling the other.

## The scenario is the contract

One file feeds both halves. Blocks are namespaced by who reads them:

```jsonc
{
  "name": "fractured-robust",
  "seed": 424242,
  "federation": {          // Python reads this
    "num_clients": 24, "rounds": 50, "dim": 32,
    "num_classes": 12, "num_samples": 12000,
    "partition": "dirichlet", "alpha": 0.05,
    "clients_per_round": 12, "lr": 0.35, "jitter": 0.08,
    "aggregator": "trimmed", "trim_beta": 0.2
  },
  "privacy": {             // Python reads this
    "clip_norm": 0.8, "sigma": 0.7, "delta": 1e-6
  },
  "network": {             // Go reads this
    "base_latency_ms": 50, "jitter_ms": 25,
    "drop_prob": 0.1, "straggler_prob": 0.2,
    "straggler_extra_ms": 1200, "deadline_ms": 500,
    "partitions": [
      { "round_start": 8,  "round_end": 14, "isolated": [0,1,2,3,4] },
      { "round_start": 25, "round_end": 33, "isolated": [12,13,14,15,16,17] },
      { "round_start": 40, "round_end": 44, "isolated": [20,21,22,23] }
    ]
  }
}
```

Three bundled scenarios live in `federift/scenarios/`: `baseline-iid`,
`noniid-dp`, and `fractured-robust`.

## Running it

### Python (no install needed)

```bash
# list bundled scenarios
python -m federift scenarios

# run a scenario with a round-by-round text report
python -m federift run federift/scenarios/noniid-dp.json

# inspect the non-IID label skew a scenario produces
python -m federift partition federift/scenarios/fractured-robust.json

# just the DP accounting approximation
python -m federift privacy federift/scenarios/noniid-dp.json
```

Or install the console script:

```bash
pip install -e .
federift run federift/scenarios/baseline-iid.json
```

### Go

```bash
cd topology
go build ./...
go run ./cmd/topology -scenario ../federift/scenarios/fractured-robust.json
```
