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
row=$(grep -iE '^\|[[:space:]]*seed period[[:space:]]*\|' "$sheet" | head -n 1)
echo "${row:-no seed period row}"
# The Parameters row is | Parameter | Value | Source | Notes |: the Value cell must
# be exactly 30 s and the Source cell must cite Table 4.1 (not 4.10, 4.11, ...).
IFS='|' read -r _ _ value source _ <<<"$row"
trim() { sed "s/^[[:space:]]*//; s/[[:space:]]*$//" <<<"$1"; }
value=$(trim "$value") source=$(trim "$source")
[ "$value" = "30 s" ] || { echo "the seed period value is '$value', not '30 s'"; exit 1; }
grep -qE 'Table 4\.1([^0-9]|$)' <<<"$source" || { echo "the seed period source '$source' does not cite Table 4.1"; exit 1; }
tool=$(cd "$(dirname "$0")/../../../scripts" && pwd)/fidelity
cd "$(dirname "$sheet")" && exec "$tool" check fidelity.md
