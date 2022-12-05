"""Deterministic random helpers.

We wrap :class:`random.Random` so every stochastic step in the simulator is
seeded and reproducible. A single master seed fans out into per-client and
per-round sub-streams via stable string keys.
"""

from __future__ import annotations

