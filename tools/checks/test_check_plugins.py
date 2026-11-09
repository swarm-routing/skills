#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Self-test for check-plugins.py: this repo passes; each broken copy fails
with the expected message."""

import importlib.util
import os
import shutil
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
    for sub in (".claude-plugin", "skills"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    p = os.path.join(d, path)
    text = open(p).read()
    assert old in text, (path, old)
    open(p, "w").write(text.replace(old, new, 1))
    errs = cp.check(d)
    assert any(expect in e for e in errs), (expect, errs)
    print(f"ok    {expect}")


broken(
    "skills/org-repo/SKILL.md",
    "name: org-repo",
    "name: other",
    "frontmatter name `other`",
)
broken(
    ".claude-plugin/plugin.json",
    '"version": "0.2.0"',
    '"version": "0.3.0"',
    "version 0.3.0 != marketplace 0.2.0",
)
broken(
    ".claude-plugin/marketplace.json",
    '"source": "./"',
    '"source": "https://x"',
    "source must be a ./relative path",
)
broken(
    ".claude-plugin/marketplace.json",
    '"name": "swarm-routing",\n      "source"',
    '"name": "Swarm_Routing",\n      "source"',
    "name must be kebab-case",
)
broken(
    "skills/fidelity-sheet/SKILL.md",
    "license: MIT OR GPL-2.0-only",
    "license: MIT OR GPL-2.0-only\nversion: 1",
    "field `version` is not in the Agent Skills spec",
)
broken(
    "skills/fidelity-sheet/SKILL.md",
    "compatibility: Needs",
    "compatibility: " + "x" * 501 + " Needs",
    "compatibility must be 1-500 characters",
)
broken(
    "skills/fidelity-sheet/SKILL.md",
    "# fidelity-sheet",
    "# fidelity-sheet" + "\nfiller" * 500,
    "keep SKILL.md under 500",
)


def orphan():
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    os.makedirs(os.path.join(d, "elsewhere"))
    shutil.move(os.path.join(d, "skills", "fidelity-sheet"), os.path.join(d, "elsewhere"))
    shutil.copytree(os.path.join(d, "elsewhere", "fidelity-sheet"), os.path.join(d, "skills", "ns3--bad"))
    errs = cp.check(d)
    assert any("ns3--bad" in e and "single hyphens" in e for e in errs), errs
    print("ok    a doubled hyphen in a skill name is rejected")


orphan()
print("check-plugins self-test: OK")
