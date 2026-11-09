#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Validate the marketplace and the skills against the Agent Skills spec
(https://agentskills.io/specification, the format skills.sh installs):
.claude-plugin/marketplace.json, every plugin's .claude-plugin/plugin.json,
and every skills/<name>/SKILL.md (frontmatter fields and limits, name =
directory, executable scripts, body under 500 lines). Every skill directory
under skills/ must belong to a listed plugin. One line per problem; exit 1 if
any. Stdlib only.

Usage: check-plugins.py [REPO_DIR]
"""

import json
import os
import re
import sys

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # no leading, trailing or doubled hyphen
FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
MAX_LINES = 500


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
    seen = set()
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
            if not NAME.match(s) or len(s) > 64:
                errs.append(
                    f"{rel}: name must be 1-64 lowercase letters, digits and single hyphens"
                )
            for key in fm:
                if key not in FIELDS:
                    errs.append(f"{rel}: frontmatter field `{key}` is not in the Agent Skills spec")
            c = fm.get("compatibility")
            if c is not None and not (1 <= len(c) <= 500):
                errs.append(f"{rel}: compatibility must be 1-500 characters (is {len(c)})")
            with open(os.path.join(root, rel), encoding="utf-8") as f:
                nlines = sum(1 for _ in f)
            if nlines > MAX_LINES:
                errs.append(
                    f"{rel}: {nlines} lines; keep SKILL.md under {MAX_LINES} (move detail to references/)"
                )
            seen.add(os.path.normpath(os.path.join(sdir, s)))
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
    top = os.path.join(root, "skills")
    for s in sorted(os.listdir(top)) if os.path.isdir(top) else []:
        if os.path.normpath(os.path.join(top, s)) not in seen:
            errs.append(f"skills/{s}: not in any plugin listed in marketplace.json")
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
