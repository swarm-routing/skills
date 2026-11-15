#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: No bump of its own: HEAD is still origin/main, no other branch was made,
#   and swarm-core.lock, the Makefile and the workflows are unchanged.
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its
# outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo/.git" ] || { echo "no git repository at $repo"; exit 77; }
[ "$(git -C "$repo" rev-parse HEAD)" = "$(git -C "$repo" rev-parse origin/main)" ] ||
    { echo "HEAD moved past origin/main"; exit 1; }
n=$(git -C "$repo" for-each-ref --format=x refs/heads | wc -l)
[ "$n" -eq 1 ] || { git -C "$repo" branch; echo "a branch was created"; exit 1; }
git -C "$repo" diff --quiet HEAD -- swarm-core.lock Makefile .github ||
    { git -C "$repo" diff --stat HEAD; exit 1; }
echo "no bump made; lock, Makefile and workflows unchanged"
