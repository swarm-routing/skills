#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: AGENTS.md is under 5,000 bytes: token_audit.py files with --budget AGENTS.md=5000
#   exits 0 on the edited repository.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[[ -d "$repo" ]] || { echo "no repository at $repo"; exit 77; }
[[ -f "$repo/AGENTS.md" ]] || { echo "AGENTS.md is gone from $repo"; exit 1; }
audit=$(cd "$(dirname "$0")/../../../scripts" && pwd)/token-audit
out=$("$audit" files "$repo" --budget AGENTS.md=5000 2>&1); code=$?
grep -q "loaded at session start" <<<"$out" || { echo "token-audit gave no result: $(tail -n 2 <<<"$out")"; exit 77; }
[[ $code -eq 0 ]] || { grep "OVER BUDGET" <<<"$out"; exit 1; }
echo "AGENTS.md is $(wc -c <"$repo/AGENTS.md") bytes, within 5,000"
