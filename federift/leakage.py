"""Membership / leakage heuristics.

These are *diagnostic* signals, not attacks with formal guarantees. They ask a
teaching question: "how distinguishable is a participating client's update
from the crowd?" Higher distinguishability implies higher intuitive leakage
risk. Adding DP noise should visibly reduce these signals.

Two toy metrics:

- ``update_distinguishability`` : how far each client delta sits from the mean
  delta, normalised. A crude membership-inference proxy.
- ``gradient_cosine_leak``      : mean absolute cosine similarity between a
  client's raw delta and its own target -- how much the upload "points at" the
  client's private data direction.
