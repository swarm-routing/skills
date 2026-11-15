#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The agent looked for open PRs on ARA through gh (a GET of
#   repos/swarm-routing/ARA/pulls...), so it could find org-bot's bump.
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its
# outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
log=$1/.fake-gh/calls.log
[ -f "$log" ] || { echo "no .fake-gh/calls.log: the recorded gh was never called"; exit 1; }
grep -q 'repos/swarm-routing/ARA/pulls' "$log" && { echo "open PRs were read"; exit 0; }
echo "no read of repos/swarm-routing/ARA/pulls in calls.log"
exit 1
