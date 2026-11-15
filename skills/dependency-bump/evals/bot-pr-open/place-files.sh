#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture in the current directory: files/base committed on main
# (also as origin/main), a consumer locked to swarm-core v0.3.0 (real values,
# so release_lock.py verify passes and latest reports v0.4.0), and the
# recorded GitHub API in .fake-gh/ (git-ignored): org-bot's open pin PR #170.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
cp -R "$here/files/base/." .
git add -A && git commit -qm base
git update-ref refs/remotes/origin/main HEAD
cp -R "$here/files/fake-gh" .fake-gh
echo .fake-gh/ >> .git/info/exclude
chmod +x .fake-gh/gh
