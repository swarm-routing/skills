#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: docs/references.bib passes swarm-routing/.github tools/fidelity/fidelity.py
#   bib check (exit 0).
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its outputs directory.
set -u
[ -f "$1/docs/references.bib" ] || { echo "no docs/references.bib"; exit 1; }
tool=$(cd "$(dirname "$0")/../../../scripts" && pwd)/org-tool
cd "$1" && exec "$tool" fidelity bib check .
