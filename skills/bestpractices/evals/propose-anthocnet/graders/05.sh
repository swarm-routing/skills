#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: answer.md holds at least one proposal link for project 16656, every
#   link is under 6100 characters, and no link proposes an owner-only criterion.
#
# Script grader (tools/evals/grade.py): $1 the repository, $2 the run's outputs
# directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
ans=$2/answer.md
[ -f "$ans" ] || { echo "no answer.md in $2"; exit 77; }
links=$(grep -oE 'https://www\.bestpractices\.dev/en/projects/16656/passing/edit\?[^ )>"]+' "$ans")
[ -n "$links" ] || { echo "no proposal link for project 16656"; exit 1; }
rc=0
while IFS= read -r l; do
    [ "${#l}" -lt 6100 ] || { echo "link of ${#l} characters"; rc=1; }
    for c in know_secure_design know_common_errors vulnerabilities_fixed_60_days \
        vulnerabilities_critical_fixed no_leaked_credentials static_analysis_fixed; do
        if grep -qE "[?&]${c}_status=" <<<"$l"; then echo "link proposes $c"; rc=1; fi
    done
done <<<"$links"
[ "$rc" = 0 ] && echo "$(wc -l <<<"$links") link(s), none owner-only"
exit "$rc"
