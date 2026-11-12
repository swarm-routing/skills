#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: report.md names issue_read as the most-called tool, with its 72 calls.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
report=
for f in "$2/report.md" "$1/report.md"; do
    [ -f "$f" ] && { report=$f; break; }
done
[ -n "$report" ] || { echo "no report.md in the outputs or the repository"; exit 77; }
grep -q "issue_read" "$report" || { echo "report.md does not name issue_read"; exit 1; }
# next to the name, with no other number between: 72 given for another tool does not pass
grep -Eq "issue_read[^0-9]*72([^0-9]|$)|(^|[^0-9])72[^0-9]*issue_read" "$report" ||
    { echo "report.md does not give 72 calls for issue_read"; exit 1; }
echo "report.md names issue_read with 72 calls"
