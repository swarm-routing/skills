#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Validate the marketplace: .claude-plugin/marketplace.json, every plugin's
.claude-plugin/plugin.json, and every SKILL.md's frontmatter. One line per
problem; exit 1 if any. Stdlib only.

Usage: check-plugins.py [REPO_DIR]
"""

import json
import os
import re
import sys

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith(" "):
            out[k.strip()] = v.strip()
    return out


def check(root):
    errs = []

    def load(path):
        try:
            with open(os.path.join(root, path), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            errs.append(f"{path}: {e}")
            return None

    mkt = load(".claude-plugin/marketplace.json")
    if mkt is None:
        return errs
    for key in ("name", "owner", "plugins"):
        if key not in mkt:
            errs.append(f"marketplace.json: missing `{key}`")
    names = set()
    for p in mkt.get("plugins", []):
        name, src = p.get("name", ""), p.get("source", "")
        where = f"marketplace.json plugin `{name}`"
        if not NAME.match(name):
            errs.append(f"{where}: name must be kebab-case")
        if name in names:
            errs.append(f"{where}: duplicate name")
        names.add(name)
        if not p.get("description"):
            errs.append(f"{where}: missing description")
        if not (isinstance(src, str) and src.startswith("./")):
            errs.append(f"{where}: source must be a ./relative path in this repo")
            continue
        pdir = os.path.normpath(os.path.join(root, src))
        manifest = load(os.path.relpath(os.path.join(pdir, ".claude-plugin/plugin.json"), root))
        if manifest is not None:
            if manifest.get("name") != name:
                errs.append(
                    f"{src}/.claude-plugin/plugin.json: name `{manifest.get('name')}` != `{name}`"
                )
            if manifest.get("version") != p.get("version"):
                errs.append(
                    f"{src}: version {manifest.get('version')} != marketplace {p.get('version')}"
                )
        sdir = os.path.join(pdir, "skills")
        skills = sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []
        if not skills:
            errs.append(f"{src}: no skills/<name>/SKILL.md")
        for s in skills:
            rel = os.path.relpath(os.path.join(sdir, s, "SKILL.md"), root)
            try:
                with open(os.path.join(root, rel), encoding="utf-8") as f:
                    fm = frontmatter(f.read())
            except OSError:
                errs.append(f"{rel}: missing")
                continue
            if fm is None:
                errs.append(f"{rel}: no --- frontmatter ---")
                continue
            if fm.get("name") != s:
                errs.append(f"{rel}: frontmatter name `{fm.get('name')}` != directory `{s}`")
            d = fm.get("description", "")
            if not d or len(d) > 1024:
                errs.append(f"{rel}: description must be 1-1024 characters (is {len(d)})")
            for script in (
                os.listdir(os.path.join(sdir, s, "scripts"))
                if os.path.isdir(os.path.join(sdir, s, "scripts"))
                else []
            ):
                sp = os.path.join(sdir, s, "scripts", script)
                if not os.access(sp, os.X_OK):
                    errs.append(f"{os.path.relpath(sp, root)}: not executable")
    return errs


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    errs = check(root)
    for e in errs:
        print(e)
    print(f"check-plugins: {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
