#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The agent read ARA's open PRs through gh (a GET of
#   repos/swarm-routing/ARA/pulls... that the recorded API served), so it
#   could find org-bot's bump.
#
# Script grader (tools/evals/grade.py): $1 is the run's repository, $2 its
# outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
log=$1/.fake-gh/served.log
[ -f "$log" ] || { echo "no .fake-gh/served.log: the recorded gh never served a read"; exit 1; }
grep -q '^repos/swarm-routing/ARA/pulls' "$log" && { echo "open PRs were read (served)"; exit 0; }
echo "no served read of repos/swarm-routing/ARA/pulls in served.log"
exit 1
