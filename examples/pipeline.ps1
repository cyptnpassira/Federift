# End-to-end federift pipeline (PowerShell).
# Go simulates the network; Python runs the federated round with those drops.
param(
    [string]$Scenario = "federift/scenarios/fractured-robust.json"
