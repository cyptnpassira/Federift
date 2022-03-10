"""federift command-line interface.

Subcommands
-----------
run       : run a scenario and print a round-by-round report.
privacy   : print only the DP accounting approximation for a scenario.
partition : inspect the non-IID label skew produced by a scenario.
scenarios : list bundled example scenarios.

Everything is stdlib-only. Reports are plain text (with an optional ``--json``
switch on ``run`` for machine consumption / piping into the Go engine).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

from . import __version__, partition, privacy, scenario as scenario_mod, simulator

_SCENARIO_DIR = os.path.join(os.path.dirname(__file__), "scenarios")


def _load_trace(path: Optional[str]) -> Optional[Dict[int, List[int]]]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # trace JSON: {"rounds": [{"round": 0, "reachable": [..]}, ...]}
    trace: Dict[int, List[int]] = {}
    for entry in data.get("rounds", []):
