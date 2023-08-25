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
