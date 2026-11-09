#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: check_docs.py no longer warns that the README has no explanation near the top.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
docs=$(cd "$(dirname "$0")/../../../scripts" && pwd)/check-docs
out=$("$docs" "$repo" 2>&1)
# no PASS/WARN/FAIL line: the tool crashed or could not fetch the org repo
grep -qE "^(PASS|WARN|FAIL) " <<<"$out" || { echo "check-docs gave no result: $(tail -n 2 <<<"$out")"; exit 77; }
grep -E "^WARN  README: no explanation" <<<"$out" && exit 1
echo "check_docs.py finds an explanation near the top"
