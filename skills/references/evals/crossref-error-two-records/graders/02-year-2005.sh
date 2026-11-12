#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: WF05 in docs/references.bib has year 2005 and keeps its DOI,
#   10.1109/sis.2005.1501641 (any letter case).
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its outputs directory.
set -u
bib="$1/docs/references.bib"
[ -f "$bib" ] || { echo "no docs/references.bib"; exit 1; }
entry=$(awk '/^@[a-zA-Z]+\{WF05,/{p=1} p{print} p&&/^\}/{exit}' "$bib")
[ -n "$entry" ] || { echo "no WF05 entry"; exit 1; }
grep -Eiq '^[[:space:]]*year[[:space:]]*=[[:space:]]*(\{2005\}|"2005"|2005[[:space:]]*(,|$))' <<<"$entry" || { echo "WF05 has no year 2005"; exit 1; }
grep -Eiq 'doi[[:space:]]*=[[:space:]]*[{"]10\.1109/sis\.2005\.1501641[}"]' <<<"$entry" ||
    { echo "WF05 lost its DOI"; exit 1; }
echo "WF05: year 2005, DOI kept"
