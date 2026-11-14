#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: .github/org-sync.toml has an [[extra_badges]] entry for "Core coverage" in the
#   quality group, with the original alt text, image and link, and the README keeps no
#   hand-written copy of it outside the badge markers.
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
repo=$1
[[ -d "$repo" ]] || { echo "no repository at $repo"; exit 77; }
python3 -I - "$repo" <<'PY'
import os
import re
import sys

try:
    import tomllib
except ImportError:
    print("tomllib needs Python 3.11+; cannot grade")
    sys.exit(77)
repo = sys.argv[1]
with open(os.path.join(repo, ".github/org-sync.toml"), "rb") as f:
    extras = tomllib.load(f).get("extra_badges", [])
img = "https://img.shields.io/endpoint?url=https%3A%2F%2Fswarm-routing.github.io%2FARA%2Fbadges%2Fcoverage.json"
link = "https://github.com/swarm-routing/ARA/actions/workflows/core.yml"
ok = any(
    e.get("group") == "quality"
    and e.get("alt") == "Core coverage"
    and e.get("image") == img
    and e.get("link") == link
    for e in extras
    if isinstance(e, dict)
)
print(f"extra_badges = {extras}")
with open(os.path.join(repo, "README.md"), encoding="utf-8") as f:
    readme = f.read()
outside = re.sub(r"<!-- org-sync:begin badges -->.*?<!-- org-sync:end badges -->", "", readme, flags=re.S)
if "coverage.json" in outside:
    print("the README still has the hand-written coverage badge outside the markers")
    ok = False
sys.exit(0 if ok else 1)
PY
