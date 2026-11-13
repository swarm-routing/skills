#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# grader: The agent read the merge queue's runs for the PR (pr-status queued: a
#   GET of actions/runs?event=merge_group on swarm-routing/ns3-tools).
#
# Script grader (tools/evals/grade.py): $1 is the run's edited repository, $2
# its outputs directory. Exit 0 pass, 77 cannot grade, else fail.
set -u
log=$1/.fake-gh/calls.log
[ -f "$log" ] || { echo "no .fake-gh/calls.log under $1: the recorded gh was never called, or the run kept no repository"; exit 77; }
if grep -q 'repos/swarm-routing/ns3-tools/actions/runs?event=merge_group' "$log"; then
    echo "the merge_group runs were read ($(grep -c 'event=merge_group' "$log") call(s))"
    exit 0
fi
echo "no read of actions/runs?event=merge_group in calls.log: pr-status queued was not run"
exit 1
