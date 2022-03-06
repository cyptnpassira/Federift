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
