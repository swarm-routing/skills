#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: AGENTS.md carries no dated status any more: outside the org-managed block it contains no
#   ISO date (2026-10-28, 2026-10-30, 2026-11-02 are gone from it).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[[ -f "$repo/AGENTS.md" ]] || { echo "no AGENTS.md in $repo"; exit 77; }
hits=$(awk '/org-sync:begin/{f=1} !f{print} /org-sync:end/{f=0}' "$repo/AGENTS.md" | grep -nE "20[0-9]{2}-[0-9]{2}-[0-9]{2}")
[[ -z "$hits" ]] || { echo "dated text left in AGENTS.md:"; echo "$hits"; exit 1; }
echo "no ISO date in AGENTS.md outside the managed block"
