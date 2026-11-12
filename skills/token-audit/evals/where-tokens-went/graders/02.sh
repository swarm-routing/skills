#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: report.md gives the context of the first request as 61,250 tokens.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
report=
for f in "$2/report.md" "$1/report.md"; do
    [ -f "$f" ] && { report=$f; break; }
done
[ -n "$report" ] || { echo "no report.md in the outputs or the repository"; exit 77; }
grep -Eq "61[,. ]?250" "$report" || { echo "report.md does not give 61,250"; exit 1; }
echo "report.md gives 61,250 for the first request"
