#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: answer.md names report_responses and cites the issue tracker by a
#   full https URL under github.com/swarm-routing/AntHocNet/issues.
#
# Script grader (tools/evals/grade.py): $1 the repository, $2 the run's outputs
# directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
[ -d "$2" ] || { echo "no outputs directory $2"; exit 77; }
ans=$2/answer.md
[ -f "$ans" ] || { echo "no answer.md in $2 (the prompt asks for it)"; exit 1; }
grep -q 'report_responses' "$ans" || { echo "report_responses not named"; exit 1; }
grep -qE 'https://github\.com/swarm-routing/AntHocNet/issues' "$ans" || { echo "no full issues URL"; exit 1; }
echo "criterion named, tracker URL cited"
