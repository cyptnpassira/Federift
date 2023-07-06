"""The federated round loop.

Each round:

  1. Select a subset of clients (deterministic per round).
  2. Each selected client computes a local delta toward its target.
  3. Deltas are L2-clipped to ``clip_norm``.
  4. The server aggregates (FedAvg / trimmed / krum).
  5. Gaussian DP noise is optionally added to the aggregate.
  6. The global model steps by the (noised) aggregate.

The simulator can optionally consume a Go-produced *network trace* to drop
stragglers/partitioned clients from a round -- coupling the privacy core to
the topology engine through the shared scenario.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import aggregate, clients, leakage, partition, privacy, rng, vectors
from .scenario import Scenario
