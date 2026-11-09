#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Builds the fixture repo in the current directory: files/base committed on
# main, then files/change copied over it and left uncommitted (the diff).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
cp -R "$here/files/base/." .
git init -q -b main . && git config user.email eval@example.org && git config user.name eval
git add -A && git commit -qm base
cp -R "$here/files/change/." .
