#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: check_docs.py passes on the edited repository with no WARN and no FAIL
#   (the broken link and the orphan page are both resolved).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
docs=$(cd "$(dirname "$0")/../../../scripts" && pwd)/check-docs
out=$("$docs" "$repo")
grep -E "^(WARN|FAIL)" <<<"$out" && exit 1
tail -n 1 <<<"$out"
