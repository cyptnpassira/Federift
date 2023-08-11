"""Minimal pure-Python vector operations.

We deliberately avoid numpy so the simulator runs on a bare stdlib install.
Vectors are plain ``list[float]``. Everything is deterministic.
"""

from __future__ import annotations

import math
