#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: No badge line is typed by hand between the `org-sync:begin badges` /
#   `org-sync:end badges` markers: the block is unchanged, or exactly what
#   org_sync.py apply renders from the edited .github/org-sync.toml.
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
now=$(block <"$repo/README.md")
[ "$now" = "$base" ] && { echo "badge block unchanged"; exit 0; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -R "$repo/." "$tmp"
sync=$(cd "$(dirname "$0")/../../../../org-repo/scripts" && pwd)/org-sync
ORG_SYNC_DIR=${ORG_SYNC_DIR:-${ORG_TOOLS_DIR:-}} "$sync" apply "$tmp" >/dev/null 2>&1
rendered=$(block <"$tmp/README.md")
[ "$now" = "$rendered" ] || { echo "the badge block differs from what org_sync.py apply renders:"; diff <(echo "$rendered") <(echo "$now"); exit 1; }
echo "badge block is org_sync.py apply's"
