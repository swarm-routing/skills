#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: answer.md points the maintainer to bestpractices.dev for ARA (the
#   registration page with ARA's repository URL, or, once ARA is registered,
#   a proposal link whose justifications cite swarm-routing/ARA), and no URL
#   in it sets know_secure_design or no_leaked_credentials.
#
# Script grader (tools/evals/grade.py): $1 the repository, $2 the run's outputs
# directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
[ -d "$2" ] || { echo "no outputs directory $2"; exit 77; }
ans=$2/answer.md
[ -f "$ans" ] || { echo "no answer.md in $2 (the prompt asks for it)"; exit 1; }
urls=$(grep -oE 'https://www\.bestpractices\.dev/[^ )>"]+' "$ans")
new=0
grep -q 'https://www\.bestpractices\.dev/en/projects/new' <<<"$urls" &&
    grep -q 'https://github\.com/swarm-routing/ARA' "$ans" && new=1
prop='/en/projects/[0-9]+/passing/edit\?.*_justification=[^&]*github\.com(%2F|/)swarm-routing(%2F|/)ARA'
[ "$new" = 1 ] || grep -qE "$prop" <<<"$urls" ||
    { echo "no registration page with ARA's URL and no proposal link for swarm-routing/ARA"; exit 1; }
if grep -qE '(know_secure_design|no_leaked_credentials)_status=' <<<"$urls"; then
    echo "a URL sets an owner-only criterion"; exit 1
fi
echo "ARA registration page or proposal link, owner-only criteria absent"
