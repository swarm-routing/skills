#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The seed period row (30 s, Table 4.1) is kept, and the fixed sheet passes
#   fidelity.py check.
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its
# outputs directory; the sheet is docs/fidelity.md in either.
set -u
sheet=$1/docs/fidelity.md
[ -f "$sheet" ] || sheet=$2/docs/fidelity.md
[ -f "$sheet" ] || { echo "no docs/fidelity.md in the repository or the outputs"; exit 1; }
row=$(grep -iE '^\|[[:space:]]*seed period[[:space:]]*\|' "$sheet")
echo "${row:-no seed period row}"
case $row in
*30*'Table 4.1'*) ;;
*) echo "the seed period row is not 30 s from Table 4.1"; exit 1 ;;
esac
tool=$(cd "$(dirname "$0")/../../../scripts" && pwd)/fidelity
cd "$(dirname "$sheet")" && exec "$tool" check fidelity.md
