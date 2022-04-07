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
        trace[int(entry["round"])] = [int(x) for x in entry.get("reachable", [])]
    return trace


def _bar(value: float, width: int = 24, vmax: float = 1.0) -> str:
    filled = int(round(min(value, vmax) / vmax * width)) if vmax > 0 else 0
    return "#" * filled + "." * (width - filled)


def cmd_run(args: argparse.Namespace) -> int:
    sc = scenario_mod.load(args.scenario)
    trace = _load_trace(args.trace)
    result = simulator.run(sc, network_trace=trace)

    if args.json:
        payload = {
            "summary": result.summary(),
            "rounds": [vars(r) for r in result.rounds],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"federift run :: scenario='{sc.name}' seed={sc.seed}")
    print(f"  clients={sc.num_clients} rounds={sc.rounds} dim={sc.dim} "
          f"aggregator={sc.aggregator} partition={sc.partition}")
    if trace is not None:
        print(f"  network trace: {len(trace)} rounds loaded from {args.trace}")
    print("-" * 72)
    print(f"{'rnd':>3} {'part':>4} {'drop':>4} {'step':>8} {'converge':>9}  leak-dist")
    for r in result.rounds:
        print(f"{r.round_idx:>3} {r.participants:>4} {r.dropped:>4} "
              f"{r.step_norm:>8.4f} {r.convergence:>9.4f}  "
              f"{_bar(r.mean_distinguishability)}")
    print("-" * 72)
    print(f"final convergence (mean global->target L2): {result.final_convergence:.4f}")

    if result.privacy_report:
        pr = result.privacy_report
        print("\nprivacy (APPROXIMATE -- not a guarantee):")
        print(f"  sigma={pr['sigma']}  delta={pr['delta']}  rounds={pr['rounds']}")
        print(f"  eps/round ~= {pr['eps_per_round']:.4f}")
        print(f"  eps total (naive)    ~= {pr['eps_total_naive']:.4f}")
        print(f"  eps total (advanced) ~= {pr['eps_total_advanced']:.4f}")
    else:
        print("\nprivacy: sigma=0 -> no DP noise added (non-private baseline).")

