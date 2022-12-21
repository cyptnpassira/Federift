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
