#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: .github/org-sync.toml lists `arena` and `ns3dev` in `badges` (the site page
#   and the ns-3 image are linked through the org-sync badge configuration).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[ -d "$repo" ] || { echo "no repository at $repo"; exit 77; }
python3 -I - "$repo/.github/org-sync.toml" <<'PY'
import sys

try:
    import tomllib
except ImportError:
    print("tomllib needs Python 3.11+; cannot grade")
    sys.exit(77)
with open(sys.argv[1], "rb") as f:
    badges = tomllib.load(f).get("badges", [])
print(f"badges = {badges}")
sys.exit(0 if {"arena", "ns3dev"} <= set(badges) else 1)
PY
