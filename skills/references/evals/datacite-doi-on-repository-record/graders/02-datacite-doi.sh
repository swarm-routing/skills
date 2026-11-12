#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: PG460 in docs/references.bib has doi 10.17877/DE290R-14312 (any letter
#   case) and keeps role implemented.
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its outputs directory.
set -u
bib="$1/docs/references.bib"
[ -f "$bib" ] || { echo "no docs/references.bib"; exit 1; }
entry=$(awk '/^@[a-z]+\{PG460,/{p=1} p{print} p&&/^\}/{exit}' "$bib")
[ -n "$entry" ] || { echo "no PG460 entry"; exit 1; }
grep -Eiq 'doi[[:space:]]*=[[:space:]]*[{"]10\.17877/de290r-14312[}"]' <<<"$entry" ||
    { echo "PG460 has no doi 10.17877/DE290R-14312"; exit 1; }
grep -Eq 'keywords[[:space:]]*=[[:space:]]*[{"][^}"]*implemented' <<<"$entry" ||
    { echo "PG460 lost role implemented"; exit 1; }
echo "PG460: DataCite DOI, role implemented"
