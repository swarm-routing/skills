#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The first rcapa command in actions.md is `open` for sim-tools with
#   --kind ns3, before any `log` (ticket first, then the investigation).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
f=$1/actions.md
[ -f "$f" ] || { echo "no actions.md under $1"; exit 77; }
first=$(grep -E '(^|[ /])rcapa(\.py)? +(open|log|steps|doc)\b' "$f" | head -n 1)
[ -n "$first" ] || { echo "no rcapa command in actions.md"; exit 1; }
case "$first" in
    *" open "*) ;;
    *) echo "the first rcapa command is not open: $first"; exit 1 ;;
esac
case "$first" in
    *"--repo sim-tools"*"--kind ns3"* | *"--kind ns3"*"--repo sim-tools"*) echo "first rcapa command opens the ticket: $first"; exit 0 ;;
esac
echo "the open command lacks --repo sim-tools or --kind ns3: $first"
exit 1
