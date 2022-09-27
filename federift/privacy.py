"""Differential-privacy noise and *approximate* accounting.

WARNING -- READ THIS
====================
The accounting below uses well-known *closed-form approximations* (the basic
Gaussian-mechanism bound and naive/advanced composition). These are teaching
tools. They are NOT a substitute for a real privacy accountant (RDP / PLD /
moments accountant). Do not cite numbers from this module as a privacy
guarantee for anything real. See the DISCLAIMER in the README.

We model the standard DP-SGD-flavoured pipeline:
