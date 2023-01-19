"""Shared JSON scenario schema.

A *scenario* is the single source of truth shared between the Python privacy
core and the Go topology engine. Both read the same file. The Python side uses
the ``federation`` + ``privacy`` blocks; the Go engine uses the ``network``
block. Fields it doesn't recognise are ignored on each side, so the two tools
stay loosely coupled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Scenario:
    name: str
    seed: int
    federation: Dict[str, Any] = field(default_factory=dict)
    privacy: Dict[str, Any] = field(default_factory=dict)
    network: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    # ---- federation getters (with defaults) --------------------------------
    @property
    def num_clients(self) -> int:
        return int(self.federation.get("num_clients", 10))

    @property
    def rounds(self) -> int:
        return int(self.federation.get("rounds", 20))

    @property
    def dim(self) -> int:
        return int(self.federation.get("dim", 16))

    @property
    def num_classes(self) -> int:
        return int(self.federation.get("num_classes", 10))

    @property
    def num_samples(self) -> int:
        return int(self.federation.get("num_samples", 5000))

    @property
    def partition(self) -> str:
        return str(self.federation.get("partition", "dirichlet"))

    @property
    def alpha(self) -> float:
        return float(self.federation.get("alpha", 0.5))

    @property
    def clients_per_round(self) -> int:
        return int(self.federation.get("clients_per_round", self.num_clients))

    @property
    def lr(self) -> float:
        return float(self.federation.get("lr", 0.5))

    @property
    def jitter(self) -> float:
        return float(self.federation.get("jitter", 0.05))

    @property
    def aggregator(self) -> str:
        return str(self.federation.get("aggregator", "fedavg"))
