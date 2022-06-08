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

        Each class contributes a fixed pseudo-random basis vector scaled by its
        (normalised) frequency. Clients with similar label mixes end up with
        similar targets -- which is exactly the correlation membership attacks
        try to exploit.
        """
        total = self.num_samples or 1
        acc = vectors.zeros(self.dim)
        for cls in range(self.num_classes):
            freq = self.counts.get(cls, 0) / total
            if freq == 0.0:
                continue
            basis = rng.gaussian_vector(
                rng.stream(self.master_seed, "class-basis", cls), self.dim, 1.0
            )
            acc = vectors.add(acc, vectors.scale(basis, freq))
        return acc

    def local_update(
        self,
        global_model: Vector,
        lr: float,
        jitter: float,
        round_idx: int,
    ) -> Vector:
        """Return the *delta* (update) this client would upload.

        delta = lr * (target - global) + noise
        """
        tgt = self.target()
        pull = vectors.scale(vectors.sub(tgt, global_model), lr)
        if jitter > 0.0:
            r = rng.stream(self.master_seed, "jitter", self.cid, round_idx)
            noise = rng.gaussian_vector(r, self.dim, jitter)
