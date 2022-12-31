"""Shared JSON scenario schema.

A *scenario* is the single source of truth shared between the Python privacy
core and the Go topology engine. Both read the same file. The Python side uses
the ``federation`` + ``privacy`` blocks; the Go engine uses the ``network``
block. Fields it doesn't recognise are ignored on each side, so the two tools
stay loosely coupled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Scenario:
    name: str
    seed: int
    federation: Dict[str, Any] = field(default_factory=dict)
    privacy: Dict[str, Any] = field(default_factory=dict)
    network: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    # ---- federation getters (with defaults) --------------------------------
    @property
    def num_clients(self) -> int:
        return int(self.federation.get("num_clients", 10))

    @property
    def rounds(self) -> int:
        return int(self.federation.get("rounds", 20))

    @property
    def dim(self) -> int:
        return int(self.federation.get("dim", 16))

    @property
    def num_classes(self) -> int:
        return int(self.federation.get("num_classes", 10))

    @property
    def num_samples(self) -> int:
