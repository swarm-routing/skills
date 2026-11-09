#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
set -eu
mkdir -p docs
cp "$(dirname "$0")/files/fidelity.md" docs/fidelity.md
