#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: answer.md holds a bestpractices.dev registration URL for ARA, and no
#   URL in it sets know_secure_design or no_leaked_credentials.
#
# Script grader (tools/evals/grade.py): $1 the repository, $2 the run's outputs
# directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
ans=$2/answer.md
[ -f "$ans" ] || { echo "no answer.md in $2"; exit 77; }
urls=$(grep -oE 'https://www\.bestpractices\.dev/[^ )>"]+' "$ans")
grep -qE 'url=https?%3A%2F%2Fgithub\.com%2Fswarm-routing%2FARA|url=https://github\.com/swarm-routing/ARA' <<<"$urls" ||
    { echo "no registration URL for swarm-routing/ARA"; exit 1; }
if grep -qE '(know_secure_design|no_leaked_credentials)_status=' <<<"$urls"; then
    echo "a URL sets an owner-only criterion"; exit 1
fi
echo "registration URL present, owner-only criteria absent"
