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

    if result.leakage_report:
        lk = result.leakage_report
        print("\nleakage heuristics (diagnostic only):")
        print(f"  mean distinguishability = {lk['mean_distinguishability']:.4f}")
        print(f"  max  distinguishability = {lk['max_distinguishability']:.4f}")
        print(f"  mean cosine leak        = {lk['mean_cosine_leak']:.4f}")
        print(f"  most-exposed client     = #{lk['most_exposed_client']}")
    return 0


def cmd_privacy(args: argparse.Namespace) -> int:
    sc = scenario_mod.load(args.scenario)
    if sc.sigma <= 0.0:
        print("sigma <= 0: no noise, epsilon is unbounded (non-private).")
        return 0
    rep = privacy.account(sc.sigma, sc.clip_norm, sc.delta, sc.rounds)
    print(json.dumps(rep.as_dict(), indent=2))
    return 0


def cmd_partition(args: argparse.Namespace) -> int:
    sc = scenario_mod.load(args.scenario)
    if sc.partition == "iid":
        parts = partition.iid_partition(sc.num_clients, sc.num_samples, sc.num_classes, sc.seed)
    else:
        parts = partition.dirichlet_partition(
            sc.num_clients, sc.num_samples, sc.num_classes, sc.alpha, sc.seed
        )
    print(f"partition='{sc.partition}' clients={sc.num_clients} classes={sc.num_classes}")
    print("-" * 60)
    for cid, counts in enumerate(parts):
        skew = partition.skew_index(counts, sc.num_classes)
        total = sum(counts.values())
        print(f"client {cid:>3}: n={total:>5} skew={skew:5.3f}  {_bar(skew)}")
    avg = sum(partition.skew_index(c, sc.num_classes) for c in parts) / max(1, len(parts))
    print("-" * 60)
    print(f"mean skew index: {avg:.4f} (0=uniform, 1=single-class)")
    return 0


def cmd_scenarios(_args: argparse.Namespace) -> int:
    if not os.path.isdir(_SCENARIO_DIR):
        print("no bundled scenarios found.")
        return 0
    print("bundled scenarios:")
    for name in sorted(os.listdir(_SCENARIO_DIR)):
        if name.endswith(".json"):
