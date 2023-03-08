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
    r = rng.stream(master_seed, "partition", "iid")
    labels = [i % num_classes for i in range(num_samples)]
    r.shuffle(labels)
    per = num_samples // num_clients
    out: List[Dict[int, int]] = []
    for c in range(num_clients):
        start = c * per
        end = num_samples if c == num_clients - 1 else start + per
        counts: Dict[int, int] = {}
        for lab in labels[start:end]:
            counts[lab] = counts.get(lab, 0) + 1
        out.append(counts)
    return out


def dirichlet_partition(
    num_clients: int,
    num_samples: int,
    num_classes: int,
    alpha: float,
    master_seed: int,
) -> List[Dict[int, int]]:
    """Non-IID label-skew partition via a Dirichlet(alpha) prior per client."""
    r = rng.stream(master_seed, "partition", "dirichlet", alpha)
    out: List[Dict[int, int]] = []
    remaining = num_samples
    for c in range(num_clients):
        clients_left = num_clients - c
        share = remaining // clients_left if clients_left > 0 else remaining
        remaining -= share
        props = _dirichlet(r, [alpha] * num_classes)
        counts: Dict[int, int] = {}
        assigned = 0
        for cls in range(num_classes):
            n = int(round(props[cls] * share))
            if n > 0:
                counts[cls] = n
                assigned += n
        # patch rounding drift onto the dominant class
        if assigned != share and props:
            dominant = max(range(num_classes), key=lambda k: props[k])
            counts[dominant] = max(0, counts.get(dominant, 0) + (share - assigned))
        out.append(counts)
    return out


def skew_index(counts: Dict[int, int], num_classes: int) -> float:
    """Return a 0..1 skew score (0 = uniform over classes, ~1 = single class).

    Computed as normalised entropy deficit.
    """
    total = sum(counts.values())
    if total == 0 or num_classes <= 1:
        return 0.0
    entropy = 0.0
    for cls in range(num_classes):
        p = counts.get(cls, 0) / total
        if p > 0:
            entropy -= p * math.log(p)
    max_entropy = math.log(num_classes)
