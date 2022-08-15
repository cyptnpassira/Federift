"""Membership / leakage heuristics.

These are *diagnostic* signals, not attacks with formal guarantees. They ask a
teaching question: "how distinguishable is a participating client's update
from the crowd?" Higher distinguishability implies higher intuitive leakage
risk. Adding DP noise should visibly reduce these signals.

Two toy metrics:

- ``update_distinguishability`` : how far each client delta sits from the mean
  delta, normalised. A crude membership-inference proxy.
- ``gradient_cosine_leak``      : mean absolute cosine similarity between a
  client's raw delta and its own target -- how much the upload "points at" the
  client's private data direction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence

from . import vectors
from .vectors import Vector


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    na = vectors.norm(a)
    nb = vectors.norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return vectors.dot(a, b) / (na * nb)


def update_distinguishability(deltas: Sequence[Vector]) -> List[float]:
    """Per-client normalised distance from the aggregate delta (0..~1+)."""
    if not deltas:
        return []
    center = vectors.mean(deltas)
    dists = [vectors.l2_distance(d, center) for d in deltas]
    spread = max(dists) or 1.0
    return [d / spread for d in dists]


def gradient_cosine_leak(deltas: Sequence[Vector], targets: Sequence[Vector]) -> List[float]:
    """Absolute cosine alignment between each delta and its client target."""
    return [abs(_cosine(d, t)) for d, t in zip(deltas, targets)]


@dataclass
class LeakageReport:
    mean_distinguishability: float
    max_distinguishability: float
    mean_cosine_leak: float
    most_exposed_client: int

    def as_dict(self) -> dict:
        return {
            "mean_distinguishability": self.mean_distinguishability,
            "max_distinguishability": self.max_distinguishability,
            "mean_cosine_leak": self.mean_cosine_leak,
            "most_exposed_client": self.most_exposed_client,
            "note": "Heuristic leakage signals; not a formal attack success rate.",
        }

