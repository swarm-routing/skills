#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The repository's own rules 4 to 8 are still in AGENTS.md itself (the always-loaded
#   file), each with its operative sentence, not moved to a document read on demand.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -f "$repo/AGENTS.md" ] || { echo "no AGENTS.md in $repo"; exit 77; }
missing=0
for phrase in "never includes a simulator header" "carries a core unit test" "append-only" "kTraceVersion" "stay bounded" "Papers stay out"; do
    grep -qF "$phrase" "$repo/AGENTS.md" || { echo "missing from AGENTS.md: $phrase"; missing=1; }
done
[ $missing -eq 0 ] || exit 1
echo "rules 4-8 are all in AGENTS.md"
