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
