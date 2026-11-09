#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: No core/ or ns3/ directory is created: the layout is marked planned, not
#   made true with empty directories.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
for d in core ns3; do
    [ -e "$repo/$d" ] && { echo "$d/ exists"; exit 1; }
done
echo "no core/ or ns3/"
