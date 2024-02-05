# End-to-end federift pipeline (PowerShell).
# Go simulates the network; Python runs the federated round with those drops.
param(
    [string]$Scenario = "federift/scenarios/fractured-robust.json"
)
$ErrorActionPreference = "Stop"

$root  = Split-Path -Parent $PSScriptRoot
$trace = Join-Path $root "trace.json"

