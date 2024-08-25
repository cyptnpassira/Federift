"""Minimal pure-Python vector operations.

We deliberately avoid numpy so the simulator runs on a bare stdlib install.
Vectors are plain ``list[float]``. Everything is deterministic.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence

Vector = List[float]


def zeros(dim: int) -> Vector:
    return [0.0] * dim


def add(a: Sequence[float], b: Sequence[float]) -> Vector:
    _check(a, b)
    return [x + y for x, y in zip(a, b)]


def sub(a: Sequence[float], b: Sequence[float]) -> Vector:
    _check(a, b)
    return [x - y for x, y in zip(a, b)]


def scale(a: Sequence[float], s: float) -> Vector:
    return [x * s for x in a]


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    _check(a, b)
    return math.fsum(x * y for x, y in zip(a, b))


def norm(a: Sequence[float]) -> float:
    return math.sqrt(math.fsum(x * x for x in a))


def l2_distance(a: Sequence[float], b: Sequence[float]) -> float:
    _check(a, b)
    return math.sqrt(math.fsum((x - y) ** 2 for x, y in zip(a, b)))


def mean(vectors: Sequence[Sequence[float]]) -> Vector:
    if not vectors:
        raise ValueError("cannot average an empty set of vectors")
    dim = len(vectors[0])
    acc = zeros(dim)
    for v in vectors:
        if len(v) != dim:
            raise ValueError("dimension mismatch in mean()")
        for i, x in enumerate(v):
            acc[i] += x
    n = float(len(vectors))
    return [x / n for x in acc]


def weighted_mean(vectors: Sequence[Sequence[float]], weights: Sequence[float]) -> Vector:
    if len(vectors) != len(weights):
        raise ValueError("vectors/weights length mismatch")
    if not vectors:
        raise ValueError("cannot average an empty set")
    total = math.fsum(weights)
    if total <= 0:
        raise ValueError("weights must sum to a positive number")
    dim = len(vectors[0])
    acc = zeros(dim)
    for v, w in zip(vectors, weights):
        for i, x in enumerate(v):
            acc[i] += x * w
    return [x / total for x in acc]


def clip_l2(a: Sequence[float], max_norm: float) -> Vector:
    """Clip a vector to a maximum L2 norm (the classic DP-SGD clip)."""
    n = norm(a)
    if n <= max_norm or n == 0.0:
        return list(a)
    factor = max_norm / n
    return [x * factor for x in a]


def _check(a: Sequence[float], b: Sequence[float]) -> None:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")


def as_floats(values: Iterable) -> Vector:
    return [float(x) for x in values]
