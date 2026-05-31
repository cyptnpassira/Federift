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

### The handshake: Go network feeds Python privacy

```bash
# 1) Go simulates the network and writes a reachability trace
cd topology
go run ./cmd/topology \
    -scenario ../federift/scenarios/fractured-robust.json \
    -emit-trace ../trace.json

# 2) Python runs the federated round, honouring exactly those drops
cd ..
python -m federift run federift/scenarios/fractured-robust.json --trace trace.json
```

Now the `drop` column in Python's report matches the partitions Go scheduled.
Convergence stalls during an isolation window, then recovers. A one-shot script
in `examples/` runs both steps: `examples/pipeline.sh` (POSIX) or
`examples/pipeline.ps1` (PowerShell).

## Reading the numbers

<img src="docs/assets/privacy.svg" alt="A convergence curve descending toward client targets alongside a leakage-signal band that shrinks as the sigma noise dial turns up" width="640" />

- **convergence**: mean L2 distance between the global model and every client's
  private target. It goes down as the federation agrees. DP noise and dropped
  clients slow it.
- **leak-dist (distinguishability)**: how far each client's clipped update sits
  from the crowd's average update, normalised. A crude membership-inference
  proxy: an update that is easy to pick out is intuitively easier to detect.
- **cosine leak**: how strongly a raw update points along the client's own
  private target direction. Turning up `sigma` should push both leakage signals
  down, and convergence up (that is, worse: the trade-off).
- **epsilon**: printed only when `sigma > 0`. Computed from the classic
  Gaussian-mechanism bound and composed with both the naive and advanced
  composition theorems; federift reports the smaller. These are teaching
  approximations.

### A worked reading

From `fractured-robust` with the Go trace applied you will see something like:

```
rnd part drop     step  converge  leak-dist
 10    3    9   3.34xx    x.xxxx   #######################   <- partition window
 ...
 34   11    1   x.xxxx    x.xxxx   #####..........          <- healthy round
```

During rounds 8 to 14, 25 to 33, and 40 to 44 the isolated clusters vanish from
`part` and the `drop` count spikes: the Go partition schedule bleeding into the
Python learning loop. Convergence flattens while the network is fractured and
resumes once the island rejoins.

## The honest part (read twice)

federift is built to be pedagogically honest, so here is the fine print in
plain language.

1. **This is not a privacy proof.** The `(epsilon, delta)` values come from
   closed-form sufficient conditions (the Dwork and Roth Gaussian-mechanism
   bound, plus naive and advanced composition). They are loose. Real
   deployments use an RDP, PLD, or moments accountant that gives far tighter,
   and differently shaped, guarantees. Do not quote federift's epsilon anywhere
   that matters.
2. **The clients do not learn anything real.** There is no dataset, no loss
   surface, no gradient of a real model. A client update is a deterministic
   pull toward a fixed pseudo-random target vector. This is enough to study
   aggregation dynamics, non-IID skew, and drop behaviour, and nothing more.
3. **The leakage metrics are heuristics, not attacks.** Distinguishability and
   cosine leak are intuition-builders. They are not calibrated attack success
   rates and should not be read as such.
4. **The network model is a toy.** Independent per-client latency and drop
   draws, no shared congestion, no TCP, no real topology graph. It teaches the
   shape of stragglers and partitions, not their true statistics.
5. **Determinism over realism.** Everything is seeded so runs reproduce
   exactly. That is great for teaching and a poor model of a chaotic real
   network.

If you want the real thing: read the FedAvg paper (McMahan et al. 2017), the
DP-SGD paper (Abadi et al. 2016), and use a maintained DP accounting library.
federift is the sketch you draw before reaching for those.

## Concepts, quickly

- **round**: one full cycle. Select clients, local update, clip, aggregate,
  optionally add DP noise, step the global model.
- **non-IID**: clients hold skewed label mixes. federift produces this with a
  Dirichlet(alpha) prior; small alpha means extreme skew (a client may own one
  class), large alpha approaches IID. The `partition` subcommand prints a
  per-client `skew` score (0 uniform, 1 single class) so you can see what alpha
  bought you.
- **clipping (C)**: each client update is projected to L2 norm at or below
  `clip_norm` before it leaves. This bounds any single client's influence and
  is the precondition that makes the Gaussian noise calibration meaningful.
- **sigma**: the DP noise multiplier. Server-side Gaussian noise of scale
  `sigma * clip_norm` is added to the aggregate. `sigma = 0` is the non-private
  baseline, and federift says so.
- **trimmed mean, beta**: a robustness knob. With `aggregator: "trimmed"` and
  `trim_beta: 0.2`, the top and bottom 20 percent of values are dropped per
  coordinate before averaging, cheap insurance against a few wild updates.
- **deadline**: the Go engine marks any client whose simulated latency exceeds
  `deadline_ms` as effectively dropped. Stragglers routinely blow past it; that
  is how a heavy latency tail turns into missing contributors.

## Extending it

Because the two halves only agree on JSON, extension is local:

- **New aggregator?** Add a function to `federift/aggregate.py` and a branch in
  `simulator._aggregate`. The Go side never needs to know.
- **New network effect?** Add a field under `network` in a scenario and read it
  in `topology/engine`. Python ignores it.
- **Different client dynamics?** Rewrite `Client.local_update`. Everything
  downstream (clipping, aggregation, leakage) is agnostic to how the delta was
  produced, as long as it is a `list[float]` of the right dimension.
- **Tighter privacy accounting?** `privacy.account` is the single seam. Swap
  the closed-form bound for a real accountant and every report updates. Doing
  this properly is exactly the exercise federift is trying to motivate.

The design rule: the scenario file is the only contract. If a change would
force both languages to recompile in lockstep, it probably belongs on one side
only.

## Layout

```
federift/
├─ federift/                 Python package (stdlib only)
│  ├─ scenarios/             shared JSON scenarios
│  ├─ vectors.py aggregate.py privacy.py leakage.py ...
│  └─ cli.py __main__.py
├─ topology/                 Go module (stdlib only)
│  ├─ scenario/  engine/  cmd/topology/
│  └─ go.mod
├─ examples/                 runnable pipeline scripts
├─ docs/                     design notes and SVG assets
├─ pyproject.toml  Makefile  .github/workflows/ci.yml
└─ CHANGELOG.md  ROADMAP.md  LICENSE
```

## Make targets

```bash
make build      # go build plus python compile check
make run        # run the fractured-robust scenario end to end
make pipeline   # go emit-trace then python run --trace
make clean      # remove build artifacts and traces
```

## License and status

MIT, see [LICENSE](LICENSE). No tests ship with this project by design: it is a
compact teaching artifact, and every claim above was verified by compiling and
running both halves. Milestones that are done live in [ROADMAP.md](ROADMAP.md);
the change history is in [CHANGELOG.md](CHANGELOG.md).

<div align="center"><sub>federift · break the network, watch the privacy · educational only</sub></div>

# draft note 73
