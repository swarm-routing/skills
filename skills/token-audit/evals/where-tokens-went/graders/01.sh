#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: report.md gives the number of API requests as 40 (one per unique message; the
#   transcript's assistant lines number more, because each content block is its own line).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
report=
for f in "$2/report.md" "$1/report.md"; do
    [[ -f "$f" ]] && { report=$f; break; }
done
[[ -n "$report" ]] || { echo "no report.md in the outputs or the repository"; exit 77; }
grep -Eiq "(^|[^0-9])40([^0-9,]|$).{0,40}request|request.{0,40}(^|[^0-9])40([^0-9,]|$)" "$report" || { echo "report.md does not say 40 requests"; exit 1; }
echo "report.md says 40 requests"
