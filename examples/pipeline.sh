#!/usr/bin/env bash
# End-to-end federift pipeline: Go simulates the network, Python runs the
# federated round honouring the resulting drops/partitions.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCEN="${1:-federift/scenarios/fractured-robust.json}"
