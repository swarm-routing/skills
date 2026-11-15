#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture in the current directory: a repository that adopted
# reusable-release.yml (caller, .cz.toml at 0.4.0, make dist) whose
# docs/roadmap.md has no v0.5.0 row, committed on main (also as origin/main),
# and the recorded GitHub API in .fake-gh/ (git-ignored): no open
# release:v0.5.0 issue, no open bot/release PR.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
cp -R "$here/files/base/." .
git add -A && git commit -qm base
git update-ref refs/remotes/origin/main HEAD
cp -R "$here/files/fake-gh" .fake-gh
echo .fake-gh/ >> .git/info/exclude
chmod +x .fake-gh/gh
