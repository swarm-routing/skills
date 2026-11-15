#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture in the current directory: a repository with a
# sonar-project.properties and the flagged script, committed on main (also as
# origin/main), and the finding as SonarQube Cloud reported it (finding.txt,
# git-ignored).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
cp -R "$here/files/base/." .
git add -A && git commit -qm base
git update-ref refs/remotes/origin/main HEAD
cp "$here/files/finding.txt" finding.txt
echo finding.txt >> .git/info/exclude
