"""Server-side aggregation rules.

- ``fedavg``       : sample-weighted mean of client deltas (McMahan et al.).
- ``trimmed_mean`` : coordinate-wise mean after dropping the highest/lowest
  ``beta`` fraction per dimension. A cheap Byzantine-robust baseline.

All functions take a list of client deltas and return a single aggregated
delta of the same dimension.
"""

from __future__ import annotations
