#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Self-test for check-plugins.py: this repo passes; each broken copy fails
with the expected message."""

import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("cp", os.path.join(HERE, "check-plugins.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

assert cp.check(ROOT) == [], cp.check(ROOT)
print("ok    this repo's marketplace is valid")


def broken(path, old, new, expect):
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "plugins"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    p = os.path.join(d, path)
    text = open(p).read()
    assert old in text, (path, old)
    open(p, "w").write(text.replace(old, new, 1))
    errs = cp.check(d)
    assert any(expect in e for e in errs), (expect, errs)
    print(f"ok    {expect}")


broken("plugins/org-repo/skills/org-repo/SKILL.md", "name: org-repo", "name: other", "frontmatter name `other`")
broken("plugins/org-repo/.claude-plugin/plugin.json", '"version": "0.1.0"', '"version": "0.2.0"', "version 0.2.0 != marketplace 0.1.0")
broken(".claude-plugin/marketplace.json", '"source": "./plugins/org-repo"', '"source": "https://x"', "source must be a ./relative path")
broken(".claude-plugin/marketplace.json", '"name": "org-repo"', '"name": "Org_Repo"', "name must be kebab-case")
print("check-plugins self-test: OK")
