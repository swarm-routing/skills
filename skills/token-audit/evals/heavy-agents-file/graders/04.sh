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
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
file=$(grep -rlF "seedpair.py" "$repo/docs" --include="*.md" 2>/dev/null | head -n 1)
[ -n "$file" ] || { echo "no file under docs/ holds the catalogue (seedpair.py)"; exit 1; }
for tool in trailmix.py tablefuzz.py capwatch.py bisect-run.sh; do
    grep -qF "$tool" "$file" || { echo "$file lost the entry for $tool"; exit 1; }
done
name=$(basename "$file")
grep -qF "$name" "$repo/AGENTS.md" || { echo "AGENTS.md does not name $name"; exit 1; }
echo "the catalogue is in docs/$name and AGENTS.md points to it"
