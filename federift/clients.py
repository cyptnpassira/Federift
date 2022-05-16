"""Deterministic toy-vector clients.

A client owns a *ground-truth target vector* derived from its class-count
signature. Local "training" is a deterministic pull of the current global
model toward that target, plus optional per-client jitter. There is no real
loss surface -- this is a systems/privacy teaching model, so we keep the
dynamics analytic and reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import rng, vectors
from .vectors import Vector


@dataclass
class Client:
    cid: int
    counts: Dict[int, int]
    dim: int
    num_classes: int
    master_seed: int

    @property
    def num_samples(self) -> int:
        return sum(self.counts.values())

    def target(self) -> Vector:
        """Stable per-client target vector encoding its label distribution.
