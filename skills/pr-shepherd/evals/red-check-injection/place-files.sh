#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture in the current directory: files/base committed on main
# (also as origin/main), files/change committed on the PR's branch (checked
# out), and the recorded GitHub API in .fake-gh/ (git-ignored), whose
# __HEAD__ placeholders become the branch's real head SHA. A file named
# *.noheader is the PR's file without its licence header (the defect under
# review); it lands without that suffix.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
branch=$(cat "$here/files/branch" 2>/dev/null || echo pr)
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
if [ -d "$here/files/base" ]; then cp -R "$here/files/base/." .; fi
git add -A && git commit -qm base --allow-empty
git update-ref refs/remotes/origin/main HEAD
git checkout -qb "$branch"
if [ -d "$here/files/change" ]; then cp -R "$here/files/change/." .; fi
find . -path ./.git -prune -o -name '*.noheader' -exec sh -c 'mv "$1" "${1%.noheader}"' _ {} \;
git add -A && git commit -qm "the PR's change" --allow-empty
git update-ref "refs/remotes/origin/$branch" HEAD
sha=$(git rev-parse HEAD)
cp -R "$here/files/fake-gh" .fake-gh
echo .fake-gh/ >> .git/info/exclude
chmod +x .fake-gh/gh
find .fake-gh -depth -name __HEAD__ -execdir mv __HEAD__ "$sha" \;
find .fake-gh -name '*.json' -exec sed -i.bak "s/__HEAD__/$sha/g" {} + && find .fake-gh -name '*.bak' -delete
