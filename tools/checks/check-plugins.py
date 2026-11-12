#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Validate the marketplace and the skills against the Agent Skills spec
(https://agentskills.io/specification, the format skills.sh installs):
.claude-plugin/marketplace.json, every plugin's .claude-plugin/plugin.json,
and every skills/<name>/SKILL.md (frontmatter fields and limits, name =
directory, executable scripts, body under 500 lines), and every eval grader
(skills/<name>/evals/<case>/graders/: an .md with a `type` that `claude plugin
eval` knows, or an executable .sh script grader with a `# grader:` line, run by
tools/evals/grade.py). Every skill directory under skills/ must belong to a
listed plugin. Every script under skills/*/scripts/ that fetches a repository
does it through the `cached-checkout` block, and the block is the same in all
of them (a skill installs alone, so each wrapper carries its own copy;
tools/checks/test_wrapper_cache.py tests the block). One line per problem; exit 1 if any. Stdlib only.

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
# The grader types `claude plugin eval` accepts in graders/*.md; a script
# grader is a .sh instead, which it ignores (tools/evals/grade.py runs it).
GRADER_TYPES = {"regex", "tool_order", "tool_used", "file_exists", "llm", "baseline"}
# The fetch block every wrapper carries, between these marker lines.
BLOCK = re.compile(r"^# >>> cached-checkout\b.*?^# <<< cached-checkout$", re.S | re.M)
FETCHES = re.compile(r"\bgit\b[^\n]*\b(clone|fetch)\b|XDG_CACHE_HOME")


def scalar(raw):
    """One-line YAML scalar -> (value, problem). Quoted values are decoded; a
    plain value YAML would misread (": " makes it a mapping, " #" starts a
    comment) is a problem, since loaders that parse YAML reject the skill."""
    v = raw.strip()
    if v.startswith('"'):
        try:
            return json.loads(v), None
        except json.JSONDecodeError:
            return v, "double-quoted value is not closed or has a bad escape"
    if v.startswith("'"):
        if len(v) < 2 or not v.endswith("'"):
            return v, "single-quoted value is not closed"
        return v[1:-1].replace("''", "'"), None
    if ": " in v or " #" in v or v.endswith(":"):
        return v, "plain value contains `: ` or ` #`, which YAML misreads; quote it"
    return v, None


def frontmatter(text):
    """(fields, problems), or None without a frontmatter block."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out, problems = {}, []
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith(" "):
            out[k.strip()], problem = scalar(v)
            if problem:
                problems.append(f"`{k.strip()}`: {problem}")
    return out, problems


def check_graders(root, skill_dir):
    """Problems with the graders of every eval case of one skill."""
    errs = []
    evals = os.path.join(skill_dir, "evals")
    for case in sorted(os.listdir(evals)) if os.path.isdir(evals) else []:
        gdir = os.path.join(evals, case, "graders")
        for name in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
            path = os.path.join(gdir, name)
            rel = os.path.relpath(path, root)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if name.endswith(".md"):
                fm = frontmatter(text)
                kind = fm[0].get("type") if fm else None
                if kind not in GRADER_TYPES:
                    errs.append(
                        f"{rel}: grader `type` is `{kind}`, not one of {sorted(GRADER_TYPES)}"
                        " (a script grader is a .sh)"
                    )
            elif name.endswith(".sh"):
                if not os.access(path, os.X_OK):
                    errs.append(f"{rel}: not executable")
                if not re.search(r"^#\s*grader:\s*\S", text, re.M):
                    errs.append(f"{rel}: no `# grader: <criterion>` line")
            else:
                errs.append(f"{rel}: a grader is an .md (LLM-judged) or an .sh (script)")
    return errs


def check_wrappers(root):
    """Problems with the cached-checkout block in skills/*/scripts/*."""
    errs, blocks = [], {}
    top = os.path.join(root, "skills")
    for s in sorted(os.listdir(top)) if os.path.isdir(top) else []:
        sdir = os.path.join(top, s, "scripts")
        for name in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
            rel = f"skills/{s}/scripts/{name}"
            with open(os.path.join(sdir, name), encoding="utf-8") as f:
                text = f.read()
            found = BLOCK.findall(text)
            if len(found) > 1:
                errs.append(f"{rel}: more than one cached-checkout block")
            if found:
                blocks[rel] = found[0]
            if FETCHES.search(BLOCK.sub("", text)):
                errs.append(f"{rel}: fetches or caches outside the cached-checkout block")
    if blocks:
        first, ref = next(iter(blocks.items()))
        for rel, block in blocks.items():
            if block != ref:
                errs.append(
                    f"{rel}: cached-checkout block differs from {first}'s; keep the copies identical"
                )
    return errs


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
            fm, yaml_problems = fm
            errs.extend(f"{rel}: frontmatter {p}" for p in yaml_problems)
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
            errs.extend(check_graders(root, os.path.join(sdir, s)))
    errs.extend(check_wrappers(root))
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
