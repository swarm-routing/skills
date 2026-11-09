# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only

.PHONY: check
check:
	bash tools/checks/headers.sh
	python3 -m unittest discover -s python/tests -t .
