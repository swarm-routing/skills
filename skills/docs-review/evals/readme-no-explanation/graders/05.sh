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
out=$("$docs" "$repo")
grep -E "^WARN  README: no explanation" <<<"$out" && exit 1
echo "check_docs.py finds an explanation near the top"
