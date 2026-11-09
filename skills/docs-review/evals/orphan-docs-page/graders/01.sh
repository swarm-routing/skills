#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The broken link in docs/markers.md (../python/README.md) is repointed to the
#   file that exists (../python/ns3_tool/README.md) or the sentence is rewritten; no
#   python/README.md stub is created just to make it resolve.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
[ -e "$repo/python/README.md" ] && { echo "python/README.md exists (a stub)"; exit 1; }
grep -n '](\.\./python/README\.md' "$repo/docs/markers.md" && exit 1
docs=$(cd "$(dirname "$0")/../../../scripts" && pwd)/check-docs
out=$("$docs" "$repo" 2>&1)
# no PASS/WARN/FAIL line: the tool crashed or could not fetch the org repo
grep -qE "^(PASS|WARN|FAIL) " <<<"$out" || { echo "check-docs gave no result: $(tail -n 2 <<<"$out")"; exit 77; }
grep -A3 "relative links to missing files" <<<"$out" && exit 1
echo "no python/README.md; docs/markers.md does not link it; every relative link resolves"
