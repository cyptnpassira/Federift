"""Data partitioning for federated clients.

The simulator uses a *toy classification* setup: each sample is a label in
``range(num_classes)``. We do not carry real features -- a client's "data" is
summarised by its per-class counts, which is enough to (a) drive a
deterministic local target vector and (b) study non-IID skew.

Two partitioners are provided:

- ``iid_partition``       : shuffle and split evenly.
- ``dirichlet_partition`` : Dirichlet(alpha) label skew, the standard knob for
  non-IID federated benchmarks. Small alpha => extreme skew.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List

from . import rng


def _gamma_sample(r: random.Random, k: float) -> float:
    """Marsaglia-Tsang gamma sampler (shape k, scale 1). stdlib-only."""
    if k < 1.0:
        # boost: Gamma(k) = Gamma(k+1) * U^(1/k)
        u = r.random()
        return _gamma_sample(r, k + 1.0) * (u ** (1.0 / k))
    d = k - 1.0 / 3.0
    c = 1.0 / math.sqrt(9.0 * d)
    while True:
        x = r.gauss(0.0, 1.0)
        v = (1.0 + c * x) ** 3
        if v <= 0:
            continue
        u = r.random()
        if u < 1.0 - 0.0331 * (x ** 4):
            return d * v
        if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)):
            return d * v


def _dirichlet(r: random.Random, alpha: List[float]) -> List[float]:
    samples = [_gamma_sample(r, a) for a in alpha]
    total = sum(samples)
    if total == 0:
        return [1.0 / len(alpha)] * len(alpha)
    return [s / total for s in samples]


def iid_partition(
    num_clients: int,
    num_samples: int,
    num_classes: int,
    master_seed: int,
) -> List[Dict[int, int]]:
    """Return per-client class-count dicts under an IID split."""
