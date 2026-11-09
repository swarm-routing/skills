#!/usr/bin/env bash
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
# Every tracked .py/.sh carries the copyright line and the SPDX identifier.
set -u
bad=0
for f in $(git ls-files '*.py' '*.sh') $(git ls-files --others --exclude-standard '*.py' '*.sh'); do
    head -n 3 "$f" | grep -q '^# Copyright (c) 2026 Daniel Joppi' && head -n 3 "$f" | grep -q '^# SPDX-License-Identifier: MIT OR GPL-2.0-only$' \
        || { echo "missing licence header: $f"; bad=1; }
done
exit $bad
