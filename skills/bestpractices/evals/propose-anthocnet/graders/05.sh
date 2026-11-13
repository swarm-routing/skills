#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: answer.md holds at least one proposal link for project 16656, every
#   link proposes at least one criterion's status with its justification, is
#   under 6100 characters, and proposes no owner-only criterion.
#
# Script grader (tools/evals/grade.py): $1 the repository, $2 the run's outputs
# directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
[ -d "$2" ] || { echo "no outputs directory $2"; exit 77; }
ans=$2/answer.md
[ -f "$ans" ] || { echo "no answer.md in $2 (the prompt asks for it)"; exit 1; }
links=$(grep -oE 'https://www\.bestpractices\.dev/en/projects/16656/passing/edit\?[^ )>"]+' "$ans")
[ -n "$links" ] || { echo "no proposal link for project 16656"; exit 1; }
rc=0
while IFS= read -r l; do
    [ "${#l}" -lt 6100 ] || { echo "link of ${#l} characters"; rc=1; }
    paired=0
    while IFS= read -r c; do
        [ -n "$c" ] && grep -qE "[?&]${c}_justification=[^&]" <<<"$l" && paired=1
    done < <(grep -oE '[?&][a-z0-9_]+_status=' <<<"$l" | sed -E 's/^[?&]//; s/_status=$//')
    [ "$paired" = 1 ] || { echo "a link proposes no criterion status with its justification"; rc=1; }
    for c in know_secure_design know_common_errors vulnerabilities_fixed_60_days \
        vulnerabilities_critical_fixed no_leaked_credentials static_analysis_fixed; do
        if grep -qE "[?&]${c}_status=" <<<"$l"; then echo "link proposes $c"; rc=1; fi
    done
done <<<"$links"
[ "$rc" = 0 ] && echo "$(wc -l <<<"$links") link(s), none owner-only"
exit "$rc"
