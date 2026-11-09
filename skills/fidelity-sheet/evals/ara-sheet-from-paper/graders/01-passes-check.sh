#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: docs/fidelity.md passes swarm-routing/.github tools/fidelity/fidelity.py
#   check (it prints 'fidelity check: ok').
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its
# outputs directory; the sheet is docs/fidelity.md in either.
set -u
sheet=$1/docs/fidelity.md
[ -f "$sheet" ] || sheet=$2/docs/fidelity.md
[ -f "$sheet" ] || { echo "no docs/fidelity.md in the repository or the outputs"; exit 1; }
tool=$(cd "$(dirname "$0")/../../../scripts" && pwd)/fidelity
cd "$(dirname "$sheet")" && exec "$tool" check fidelity.md
