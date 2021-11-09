"""federift — educational federated-learning network & privacy simulator.

This package implements a *toy* federated-learning pipeline using only the
Python standard library. It is designed for teaching and systems-level
experimentation, not for production ML and emphatically not as a privacy
proof. See the DISCLAIMER in ``README.md``.

Core pieces:

- :mod:`federift.vectors`      -- minimal pure-Python vector math
- :mod:`federift.clients`      -- deterministic toy-vector clients
- :mod:`federift.partition`    -- IID / non-IID data partitioning
- :mod:`federift.aggregate`    -- FedAvg and trimmed-mean aggregation
