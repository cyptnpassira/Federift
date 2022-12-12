"""Deterministic random helpers.

We wrap :class:`random.Random` so every stochastic step in the simulator is
seeded and reproducible. A single master seed fans out into per-client and
per-round sub-streams via stable string keys.
"""

from __future__ import annotations

import hashlib
import random
from typing import List


def derive_seed(master: int, *parts: object) -> int:
    """Derive a stable 63-bit seed from a master seed and label parts."""
    key = "::".join([str(master)] + [str(p) for p in parts])
