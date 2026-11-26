#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: actions.md has one `rcapa log` command for each of the steps
#   hypothesis, source, reproduce and duplicate-search on NS3-512 in
#   sim-tools, a `rcapa doc` command, and no second `rcapa open`.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
f=$1/actions.md
[ -f "$f" ] || { echo "no actions.md under $1"; exit 77; }
cmds=$(grep -E '(^|[ /])rcapa(\.py)? +(open|log|steps|doc)\b' "$f")
miss=""
for s in hypothesis source reproduce duplicate-search; do
    echo "$cmds" | grep -E ' log ' | grep -E -- "--step[ =]$s( |$)" | grep -q 'NS3-512' || miss="$miss $s"
done
if [ -n "$miss" ]; then
    echo "no rcapa log on NS3-512 for the step(s):$miss"
    exit 1
fi
echo "$cmds" | grep -qE ' doc ' || { echo "no rcapa doc command"; exit 1; }
if echo "$cmds" | grep -qE ' open '; then
    echo "an rcapa open command although NS3-512 exists"
    exit 1
fi
echo "all four steps logged on NS3-512 and the document derived, no second open"
