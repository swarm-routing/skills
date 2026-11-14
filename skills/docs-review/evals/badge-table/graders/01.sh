#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: check_docs.py passes the README's badge table and finds no badge outside it.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
docs=$(cd "$(dirname "$0")/../../../scripts" && pwd)/check-docs
out=$("$docs" "$repo" 2>&1)
grep -qE "^(PASS|WARN|FAIL) " <<<"$out" || { echo "check-docs gave no result: $(tail -n 2 <<<"$out")"; exit 77; }
# org tools from before the badge table (swarm-routing/.github#415) cannot judge it
grep -q "badge row with" <<<"$out" && { echo "org tools predate the badge table; cannot grade"; exit 77; }
grep -E "^PASS  README: badge table" <<<"$out" || { grep -iE "badge" <<<"$out"; exit 1; }
grep -E "outside the org-sync table" <<<"$out" && exit 1
echo "the badge table passes and no badge sits outside it"
