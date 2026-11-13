#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: answer.md holds a bestpractices.dev URL for ARA (the pre-filled
#   registration URL, or, once ARA is registered, a proposal link whose
#   justifications cite swarm-routing/ARA), and no URL in it sets
#   know_secure_design or no_leaked_credentials.
#
# Script grader (tools/evals/grade.py): $1 the repository, $2 the run's outputs
# directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
[ -d "$2" ] || { echo "no outputs directory $2"; exit 77; }
ans=$2/answer.md
[ -f "$ans" ] || { echo "no answer.md in $2 (the prompt asks for it)"; exit 1; }
urls=$(grep -oE 'https://www\.bestpractices\.dev/[^ )>"]+' "$ans")
reg='url=https?(%3A%2F%2F|://)github\.com(%2F|/)swarm-routing(%2F|/)ARA'
prop='/en/projects/[0-9]+/passing/edit\?.*_justification=[^&]*github\.com(%2F|/)swarm-routing(%2F|/)ARA'
grep -qE "$reg|$prop" <<<"$urls" || { echo "no registration URL or proposal link for swarm-routing/ARA"; exit 1; }
if grep -qE '(know_secure_design|no_leaked_credentials)_status=' <<<"$urls"; then
    echo "a URL sets an owner-only criterion"; exit 1
fi
echo "an ARA registration URL or proposal link, owner-only criteria absent"
