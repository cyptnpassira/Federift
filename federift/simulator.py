"""The federated round loop.

Each round:

  1. Select a subset of clients (deterministic per round).
  2. Each selected client computes a local delta toward its target.
  3. Deltas are L2-clipped to ``clip_norm``.
  4. The server aggregates (FedAvg / trimmed / krum).
  5. Gaussian DP noise is optionally added to the aggregate.
  6. The global model steps by the (noised) aggregate.

The simulator can optionally consume a Go-produced *network trace* to drop
stragglers/partitioned clients from a round -- coupling the privacy core to
the topology engine through the shared scenario.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import aggregate, clients, leakage, partition, privacy, rng, vectors
from .scenario import Scenario
from .vectors import Vector


@dataclass
class RoundStat:
    round_idx: int
    participants: int
    global_norm: float
    step_norm: float
    convergence: float          # mean L2 distance global->client targets
    mean_distinguishability: float
    mean_cosine_leak: float
    dropped: int = 0


@dataclass
class SimResult:
    scenario_name: str
    rounds: List[RoundStat] = field(default_factory=list)
    privacy_report: Optional[dict] = None
    final_convergence: float = 0.0
    leakage_report: Optional[dict] = None

    def summary(self) -> dict:
        return {
            "scenario": self.scenario_name,
            "num_rounds": len(self.rounds),
            "final_convergence": self.final_convergence,
            "privacy": self.privacy_report,
            "leakage": self.leakage_report,
        }


def _select(round_idx: int, n: int, k: int, seed: int) -> List[int]:
    if k >= n:
        return list(range(n))
    r = rng.stream(seed, "select", round_idx)
    return sorted(r.sample(range(n), k))


def _aggregate(name: str, deltas, weights, beta) -> Vector:
    if name == "fedavg":
        return aggregate.fedavg(deltas, weights)
    if name == "uniform":
        return aggregate.uniform_mean(deltas)
    if name == "trimmed":
        return aggregate.trimmed_mean(deltas, beta)
    if name == "krum":
        drop = max(1, int(round(beta * len(deltas))))
        return aggregate.krum_like(deltas, drop)
    raise ValueError(f"unknown aggregator: {name}")


def run(
    scenario: Scenario,
    network_trace: Optional[Dict[int, List[int]]] = None,
) -> SimResult:
    """Run the federated simulation for ``scenario``.

    ``network_trace`` maps ``round_idx -> [reachable_client_ids]`` (typically
    produced by the Go engine's ``--emit-trace``). Unreachable selected clients
    are treated as dropped for that round.
    """
