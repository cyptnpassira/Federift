"""Server-side aggregation rules.

- ``fedavg``       : sample-weighted mean of client deltas (McMahan et al.).
- ``trimmed_mean`` : coordinate-wise mean after dropping the highest/lowest
  ``beta`` fraction per dimension. A cheap Byzantine-robust baseline.

All functions take a list of client deltas and return a single aggregated
delta of the same dimension.
"""

from __future__ import annotations

import math
from typing import List, Sequence

from . import vectors
from .vectors import Vector


def fedavg(deltas: Sequence[Sequence[float]], weights: Sequence[float]) -> Vector:
    return vectors.weighted_mean(deltas, weights)


def uniform_mean(deltas: Sequence[Sequence[float]]) -> Vector:
    return vectors.mean(deltas)


def trimmed_mean(deltas: Sequence[Sequence[float]], beta: float) -> Vector:
    """Coordinate-wise trimmed mean.

    ``beta`` is the fraction trimmed from *each* tail. With ``k`` clients we
    drop ``floor(beta*k)`` values from both the top and bottom per coordinate.
    """
    if not deltas:
        raise ValueError("no deltas to aggregate")
    if not (0.0 <= beta < 0.5):
        raise ValueError("beta must be in [0, 0.5)")
    k = len(deltas)
    dim = len(deltas[0])
    trim = int(math.floor(beta * k))
    out: Vector = vectors.zeros(dim)
    for j in range(dim):
        column = sorted(d[j] for d in deltas)
        kept = column[trim: k - trim] if k - 2 * trim > 0 else column
        out[j] = math.fsum(kept) / len(kept)
