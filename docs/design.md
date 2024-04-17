# Design notes

This document explains *why* federift is shaped the way it is. For usage, see
the top-level README.

## Two languages, one file

The hard constraint driving the whole design: **Python and Go must never share
code, only a file.** That forces a clean contract — the scenario JSON — and
