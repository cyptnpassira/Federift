# End-to-end federift pipeline (PowerShell).
# Go simulates the network; Python runs the federated round with those drops.
param(
    [string]$Scenario = "federift/scenarios/fractured-robust.json"
)
$ErrorActionPreference = "Stop"

$root  = Split-Path -Parent $PSScriptRoot
$trace = Join-Path $root "trace.json"

Write-Host ">> [go] simulating network topology for $Scenario"
Push-Location (Join-Path $root "topology")
try {
    go run ./cmd/topology -scenario "../$Scenario" -emit-trace $trace
} finally {
    Pop-Location
}

Write-Host ">> [py] running federated round with the network trace applied"
Push-Location $root
try {
    python -m federift run $Scenario --trace $trace
