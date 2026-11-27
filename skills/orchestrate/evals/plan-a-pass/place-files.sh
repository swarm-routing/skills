#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture in the current directory: the handoff issue as it reads
# now (its last pass claims ARA v0.3.0 is still to be released), the status.py
# snapshot (ARA v0.3.0 already released; AntHocNet#410 P1; #1004 open) and
# the three tickets, committed on main.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
cp -R "$here/files/base/." .
git add -A && git commit -qm base
