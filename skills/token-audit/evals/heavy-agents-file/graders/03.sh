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
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
[ -f "$repo/AGENTS.md" ] || { echo "AGENTS.md is gone from $repo"; exit 1; }
missing=0
# the rule's name, then what it tells the agent to do: a rule cut down to its
# name passes the first and fails the second
for phrase in "never includes a simulator header" "ports" \
    "carries a core unit test" "core/test" \
    "append-only" "kTraceVersion" "trailmix.py" \
    "stay bounded" "core/config.h" \
    "Papers stay out" "DOI"; do
    grep -qF "$phrase" "$repo/AGENTS.md" || { echo "missing from AGENTS.md: $phrase"; missing=1; }
done
[ $missing -eq 0 ] || exit 1
echo "rules 4-8 are all in AGENTS.md"
