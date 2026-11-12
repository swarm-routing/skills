#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The tool catalogue is kept, not deleted: its entries are in a Markdown file under docs/,
#   and AGENTS.md names that file.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[[ -d "$repo" ]] || { echo "no repository at $repo"; exit 77; }
[[ -f "$repo/AGENTS.md" ]] || { echo "AGENTS.md is gone from $repo"; exit 1; }
# every Markdown file under docs/ is a candidate: the first that holds all the
# entries and is named in AGENTS.md passes
why="no file under docs/ holds the catalogue (seedpair.py)"
while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    lost=
    for tool in trailmix.py tablefuzz.py capwatch.py bisect-run.sh; do
        grep -qF "$tool" "$file" || { lost=$tool; break; }
    done
    name=$(basename "$file")
    if [[ -n "$lost" ]]; then
        why="$file has no entry for $lost"
    elif ! grep -qF "$name" "$repo/AGENTS.md"; then
        why="AGENTS.md does not name $name"
    else
        echo "the catalogue is in docs/$name and AGENTS.md points to it"
        exit 0
    fi
done <<<"$(grep -rlF "seedpair.py" "$repo/docs" --include="*.md" 2>/dev/null)"
echo "$why"
exit 1
