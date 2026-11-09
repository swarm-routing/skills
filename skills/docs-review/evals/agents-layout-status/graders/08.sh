#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The badge row between the org-sync badge markers is left untouched (it
#   already carries the site and image links).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
[ -d "$repo/.git" ] || { echo "no git history in $repo to compare with"; exit 77; }
block() { sed -n "/org-sync:begin badges/,/org-sync:end badges/p"; }
root=$(git -C "$repo" rev-list --max-parents=0 HEAD | tail -n 1)
base=$(git -C "$repo" show "$root:README.md" | block)
[ -f "$repo/README.md" ] || { echo "no README.md in $repo"; exit 1; }
now=$(block <"$repo/README.md")
[ -n "$base" ] || { echo "the fixture's README has no badge markers"; exit 77; }
[ "$now" = "$base" ] || { diff <(echo "$base") <(echo "$now"); exit 1; }
echo "badge block unchanged"
