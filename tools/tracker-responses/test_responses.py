#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""responses.py's self-test as a plain script, so CI runs it under coverage."""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("responses", os.path.join(HERE, "responses.py"))
responses = importlib.util.module_from_spec(spec)
spec.loader.exec_module(responses)
sys.exit(responses.main(["--self-test"]))
