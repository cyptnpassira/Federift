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
