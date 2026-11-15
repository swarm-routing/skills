#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: swarm-core.lock is byte-identical to the fixture's (no value typed by hand).
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its
# outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo/.git" ] || { echo "no git repository at $repo"; exit 77; }
git -C "$repo" diff --quiet origin/main -- swarm-core.lock || { git -C "$repo" diff origin/main -- swarm-core.lock; exit 1; }
echo "swarm-core.lock unchanged"
