#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture repository in the current directory from files/, committed
# on main (the agent files are audited and edited in the working tree).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
cp -R "$here/files/." .
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
git add -A && git commit -qm base
