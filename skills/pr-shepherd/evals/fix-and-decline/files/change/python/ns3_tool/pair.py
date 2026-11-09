# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Pair two arms' runs by seed: the per-seed deltas a paired comparison needs."""


def mean(values):
    return sum(values) / len(values)


def pair(a, b):
    """Per-seed deltas mean(b) - mean(a), over the seeds both arms ran, in seed order.

    a and b map a seed to the PDR of each run with that seed. A crashed run
    leaves its seed with an empty list.
    """
    seeds = sorted(set(a) & set(b))
    return [(s, mean(b[s]) - mean(a[s])) for s in seeds]
