"""Differential-privacy noise and *approximate* accounting.

WARNING -- READ THIS
====================
The accounting below uses well-known *closed-form approximations* (the basic
Gaussian-mechanism bound and naive/advanced composition). These are teaching
tools. They are NOT a substitute for a real privacy accountant (RDP / PLD /
moments accountant). Do not cite numbers from this module as a privacy
guarantee for anything real. See the DISCLAIMER in the README.

We model the standard DP-SGD-flavoured pipeline:

  1. clip each client delta to L2 norm C,
  2. add Gaussian noise N(0, (sigma*C)^2 * I) at the server,
  3. account for the (epsilon, delta) budget across rounds.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from . import rng, vectors
from .vectors import Vector


def add_gaussian_noise(
    vec: Vector,
    clip_norm: float,
    sigma: float,
    master_seed: int,
    round_idx: int,
) -> Vector:
    """Add N(0, (sigma*clip_norm)^2) noise to an already-aggregated vector."""
    if sigma <= 0.0:
        return list(vec)
    r = rng.stream(master_seed, "dp-noise", round_idx)
    scale = sigma * clip_norm
    noise = rng.gaussian_vector(r, len(vec), scale)
    return vectors.add(vec, noise)


def gaussian_mechanism_epsilon(sigma: float, delta: float) -> float:
    """Single-release (eps, delta) bound for the Gaussian mechanism.

    Uses the classic sufficient condition (Dwork & Roth, Appendix A):

        sigma >= sqrt(2 ln(1.25/delta)) / eps   =>   (eps, delta)-DP

    Rearranged to solve for eps at unit L2-sensitivity. This is loose; modern
    accountants give much tighter bounds.
    """
    if sigma <= 0.0:
        return float("inf")
    if not (0.0 < delta < 1.0):
        raise ValueError("delta must be in (0,1)")
    return math.sqrt(2.0 * math.log(1.25 / delta)) / sigma
