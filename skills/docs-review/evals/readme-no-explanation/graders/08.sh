#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The claim 'delivering 97 % of packets (better than AODV)' is gone from the README.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
[ -f "$repo/README.md" ] || { echo "no README.md in $repo"; exit 1; }
grep -inE '97 ?%|better than AODV' "$repo/README.md" && exit 1
echo "README.md has no 97 % or better-than-AODV claim"
