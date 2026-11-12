#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""What an AI session costs in tokens: before it starts, and after it ends.

    token_audit.py files [REPO ...] [--budget NAME=BYTES ...] [--budget-loaded BYTES]
                         [--bytes-per-token F] [--top N] [--json]
    token_audit.py transcript FILE ... [--min-calls K] [--top N] [--json]
    token_audit.py --self-test

`files` measures what a session reads before its first tool call, for each
REPO (default: the current directory): CLAUDE.md and every file it imports
with an `@path` line (AGENTS.md in this org), or AGENTS.md alone where there
is no CLAUDE.md; the name and description of every skill (`.claude/skills/`,
and `skills/` of a plugin repository), which are listed in every session, and
the skill bodies, which are read only when a skill is used. Each loaded file
is split at its `## ` headings, largest section first, with what makes a
section expensive or stale: bytes inside `org-sync:begin/end` markers (the
same text in every repository), ISO dates and `#N` issue numbers (status that
ages). It lists the Markdown files the loaded ones link to, which cost
nothing until they are opened. With several REPOs it adds the cost of a
session that has all of them attached, and the sections that are byte for
byte the same in more than one repository.

A budget makes it a gate: `--budget AGENTS.md=12000` fails any repository
whose AGENTS.md is larger, `--budget-loaded 16000` any repository that loads
more than that at session start. Exit 1 when a budget is exceeded, else 0.

Token counts of files are ESTIMATES: bytes divided by --bytes-per-token
(default 3.5). A token count is specific to a model and only its
`count_tokens` endpoint gives the exact number; this script stays offline and
sends nothing anywhere. Use the estimate to compare and to budget, not to bill.

`transcript` reads the JSONL transcript(s) of a finished Claude Code session
(the main session and its subagents) and says where the tokens went. These
numbers are MEASURED: they are the `usage` the API returned with each request
(`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`,
`output_tokens`; a request's context is the sum of the first three). It
reports the context of the first request (what the session cost before any
work), the largest context, the totals, and per tool: how many calls, how
many bytes of results came back, the largest results, and the calls repeated
with identical input. A tool called at least --min-calls times (default 20)
is listed as a candidate for a script or a data file: a model that reads the
same kind of thing a hundred times is doing a loop a program should do.

Only sizes, counts and a 60-character summary of a call's input are printed;
no file or tool-result content is. Stdlib only.
"""

import argparse
import collections
import contextlib
import hashlib
import io
import json
import math
import os
import re
import sys
import tempfile

BYTES_PER_TOKEN = 3.5
IMPORT_DEPTH = 5
MARK_BEGIN = re.compile(r"<!--\s*org-sync:begin\s+([\w.-]+)\s*-->")
MARK_END = re.compile(r"<!--\s*org-sync:end\s+([\w.-]+)\s*-->")
IMPORT = re.compile(r"(?<![\w`@])@([\w~][\w./~-]*)")
ISO_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
ISSUE = re.compile(r"#\d+\b")
MD_LINK = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
MD_CODE = re.compile(r"`([\w./-]+\.md)`")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
SECRET_KEY = re.compile(
    r"(?i)\b([\w-]*(?:token|secret|password|passwd|api[_-]?key|authorization)[\w-]*\s*[=:]\s*)\S+"
)
SECRET_VALUE = re.compile(r"[A-Za-z0-9+_=-]{24,}")


def tokens(nbytes, bpt=BYTES_PER_TOKEN):
    return math.ceil(nbytes / bpt)


def size(text):
    return len(text.encode("utf-8"))


def read(path):
    # newline="": line endings stay as they are on disk, so sizes are the file's
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def inside(repo, rel):
    """rel is a file that is really in repo: a symlink that leads out of it is not."""
    root = os.path.realpath(repo)
    full = os.path.realpath(os.path.join(repo, rel))
    return os.path.isfile(full) and os.path.commonpath([root, full]) == root


class Fences:
    """Fenced code blocks, line by line. A block closes on a fence of its own
    character, at least as long as the opening one, with nothing after it."""

    def __init__(self):
        self.open = None

    def feed(self, line):
        """True when the line is a fence or inside a block."""
        m = FENCE.match(line.rstrip("\r\n"))
        if self.open is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                self.open = (m.group(1)[0], len(m.group(1)))
                return True
            return False
        char, length = self.open
        if m and m.group(1)[0] == char and len(m.group(1)) >= length and not m.group(2).strip():
            self.open = None
        return True


def prose_lines(text):
    """The lines outside fenced code blocks (an `@path` in a code block is no import)."""
    fences = Fences()
    for line in text.splitlines():
        if not fences.feed(line):
            yield line


def imports(text):
    seen = []
    for line in prose_lines(text):
        for m in IMPORT.finditer(re.sub(r"`[^`]*`", "", line)):
            if m.group(1) not in seen:
                seen.append(m.group(1))
    return seen


def loaded_files(repo):
    """[(path relative to repo, why it is loaded)] in the order a session reads them."""
    entries = [
        p
        for p in ("CLAUDE.md", os.path.join(".claude", "CLAUDE.md"))
        if os.path.isfile(os.path.join(repo, p))
    ]
    if not entries and os.path.isfile(os.path.join(repo, "AGENTS.md")):
        return [("AGENTS.md", "entry (no CLAUDE.md)")]
    out, queue = [], [(p, "entry", 0) for p in entries]
    while queue:
        rel, why, depth = queue.pop(0)
        if rel in [r for r, _ in out]:
            continue
        out.append((rel, why))
        if depth >= IMPORT_DEPTH:
            continue
        base = os.path.dirname(rel)
        for target in imports(read(os.path.join(repo, rel))):
            child = os.path.normpath(os.path.join(base, target))
            if not child.startswith("..") and inside(repo, child):
                queue.append((child, f"imported by {rel}", depth + 1))
    return out


def sections(text):
    """[{title, bytes, managed: {block: bytes}, dates, issues}] split at `## ` headings."""
    out, title, lines, fences = [], "(top)", [], Fences()
    block = [None]  # the open org-sync block: it may start before a heading and span several

    def flush():
        if not lines:
            return
        body = "".join(lines)
        managed = collections.Counter()
        for line in lines:
            begin, end = MARK_BEGIN.search(line), MARK_END.search(line)
            if begin:
                block[0] = begin.group(1)
            if block[0]:
                managed[block[0]] += size(line)
            if end:
                block[0] = None
        out.append(
            {
                "title": title,
                "bytes": size(body),
                "managed": dict(managed),
                "dates": len(ISO_DATE.findall(body)),
                "issues": len(ISSUE.findall(body)),
                "sha": hashlib.sha256(body.strip().encode("utf-8")).hexdigest(),
            }
        )

    for line in text.splitlines(keepends=True):
        if not fences.feed(line) and line.startswith("## "):
            flush()
            title, lines = line.strip(), []
        lines.append(line)
    flush()
    return out


def skills(repo):
    """[{name, listed_bytes, body_bytes}]: the frontmatter is listed in every session."""
    out = []
    for root in (os.path.join(".claude", "skills"), "skills"):
        top = os.path.join(repo, root)
        if not os.path.isdir(top):
            continue
        for name in sorted(os.listdir(top)):
            path = os.path.join(top, name, "SKILL.md")
            if not os.path.isfile(path):
                continue
            text = read(path)
            m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
            # name and description, each with its indented continuation lines
            # (a block scalar, `description: >-`, has its text below the key)
            kept, keep = [], False
            for line in (m.group(1) if m else "").splitlines():
                if re.match(r"(name|description):", line):
                    keep = True
                elif line.strip() and not line[0].isspace():
                    keep = False
                if keep:
                    kept.append(line)
            listed = "\n".join(kept)
            out.append(
                {
                    "name": name,
                    "path": os.path.join(root, name, "SKILL.md"),
                    "listed_bytes": size(listed),
                    "body_bytes": size(text) - size(listed),
                }
            )
    return out


def linked_docs(repo, loaded):
    """Markdown files the loaded files point at: read only when a session opens them."""
    have, found = {rel for rel, _ in loaded}, {}
    for rel, _ in loaded:
        text = read(os.path.join(repo, rel))
        for target in MD_LINK.findall(text) + MD_CODE.findall(text):
            if "://" in target:
                continue
            for base in (os.path.dirname(rel), ""):
                child = os.path.normpath(os.path.join(base, target))
                full = os.path.join(repo, child)
                if not child.startswith("..") and inside(repo, child) and child not in have:
                    found[child] = os.path.getsize(full)
                    break
    return [{"path": p, "bytes": b} for p, b in sorted(found.items(), key=lambda kv: -kv[1])]


def audit_repo(repo, bpt):
    name = os.path.basename(os.path.abspath(repo)) or repo
    files = []
    for rel, why in loaded_files(repo):
        text = read(os.path.join(repo, rel))
        secs = sections(text)
        files.append(
            {
                "path": rel,
                "why": why,
                "bytes": size(text),
                "tokens": tokens(size(text), bpt),
                "managed_bytes": sum(sum(s["managed"].values()) for s in secs),
                "sections": secs,
            }
        )
    sk = skills(repo)
    listed = sum(s["listed_bytes"] for s in sk)
    loaded = sum(f["bytes"] for f in files) + listed
    return {
        "repo": name,
        "root": os.path.abspath(repo),
        "files": files,
        "skills": sk,
        "skills_listed_bytes": listed,
        "loaded_bytes": loaded,
        "loaded_tokens": tokens(loaded, bpt),
        "managed_bytes": sum(f["managed_bytes"] for f in files),
        "on_demand": linked_docs(repo, [(f["path"], f["why"]) for f in files]),
    }


def duplicates(audits):
    """Sections identical in at least two repositories: the same text paid for again."""
    groups = collections.defaultdict(list)
    for a in audits:
        for f in a["files"]:
            for s in f["sections"]:
                if s["bytes"] >= 200:
                    groups[s["sha"]].append(
                        (a["root"], f["path"], s["title"], s["bytes"], a["repo"])
                    )
    out = []
    for members in groups.values():
        # two repositories may share a directory name: the path tells them apart
        repos = [name for _, name in sorted({(m[0], m[4]) for m in members})]
        if len(repos) > 1:
            out.append(
                {
                    "title": members[0][2],
                    "file": members[0][1],
                    "bytes": members[0][3],
                    "repos": repos,
                    "repeated_bytes": members[0][3] * (len(repos) - 1),
                }
            )
    return sorted(out, key=lambda d: -d["repeated_bytes"])


def check_budgets(audits, budgets, budget_loaded):
    over = []
    for a in audits:
        for f in a["files"]:
            limit = budgets.get(os.path.basename(f["path"]))
            if limit is not None and f["bytes"] > limit:
                over.append(f"{a['repo']}: {f['path']} is {f['bytes']:,} bytes, budget {limit:,}")
        # a named file has its budget whether a session loads it or not
        loaded = {os.path.basename(f["path"]) for f in a["files"]}
        for name, limit in sorted(budgets.items()):
            path = os.path.join(a["root"], name)
            if name not in loaded and os.path.isfile(path) and os.path.getsize(path) > limit:
                over.append(
                    f"{a['repo']}: {name} is {os.path.getsize(path):,} bytes, budget {limit:,} "
                    "(not loaded at session start)"
                )
        if budget_loaded is not None and a["loaded_bytes"] > budget_loaded:
            over.append(
                f"{a['repo']}: loads {a['loaded_bytes']:,} bytes at session start, "
                f"budget {budget_loaded:,}"
            )
    return over


def print_files(audits, dups, over, bpt, top):
    for a in audits:
        print(f"== {a['repo']} ==")
        print(
            f"loaded at session start: {a['loaded_bytes']:,} bytes, about "
            f"{a['loaded_tokens']:,} tokens (estimate, {bpt:g} bytes per token)"
        )
        for f in a["files"]:
            print(f"  {f['path']:<28} {f['bytes']:>8,} bytes  {f['why']}")
        if a["skills"]:
            print(
                f"  {len(a['skills'])} skill(s) listed       {a['skills_listed_bytes']:>8,} bytes  "
                f"(bodies, read on use: {sum(s['body_bytes'] for s in a['skills']):,})"
            )
        if a["managed_bytes"] and a["loaded_bytes"]:
            print(
                f"  org-managed text: {a['managed_bytes']:,} bytes "
                f"({100 * a['managed_bytes'] // a['loaded_bytes']} %)"
            )
        rows = sorted(
            ((s, f["path"]) for f in a["files"] for s in f["sections"]),
            key=lambda r: -r[0]["bytes"],
        )[:top]
        if rows:
            print("  largest sections:")
        for s, path in rows:
            notes = []
            if s["managed"]:
                notes.append("managed " + ", ".join(sorted(s["managed"])))
            if s["dates"]:
                notes.append(f"{s['dates']} date(s)")
            if s["issues"]:
                notes.append(f"{s['issues']} issue number(s)")
            share = 100 * s["bytes"] // max(a["loaded_bytes"], 1)
            print(
                f"    {s['bytes']:>7,}  {share:>2} %  {path}  {s['title'][:48]}"
                + (f"  [{'; '.join(notes)}]" if notes else "")
            )
        if a["on_demand"]:
            print(
                f"  read on demand: {len(a['on_demand'])} linked file(s), "
                f"{sum(d['bytes'] for d in a['on_demand']):,} bytes"
            )
    if len(audits) > 1:
        total = sum(a["loaded_bytes"] for a in audits)
        managed = sum(a["managed_bytes"] for a in audits)
        repeated = sum(d["repeated_bytes"] for d in dups)
        print(f"== all {len(audits)} repositories ==")
        print(
            f"loaded with every repository attached: {total:,} bytes, about "
            f"{tokens(total, bpt):,} tokens (estimate)"
        )
        if total:
            print(f"org-managed text: {managed:,} bytes ({100 * managed // total} %)")
            print(
                f"sections identical in more than one repository: {len(dups)}, "
                f"{repeated:,} bytes paid again ({100 * repeated // total} %)"
            )
        for d in dups[:top]:
            print(
                f"    {d['repeated_bytes']:>7,}  {d['bytes']:,} x {len(d['repos'])} repositories  "
                f"{d['file']}  {d['title'][:48]}"
            )
    for line in over:
        print(f"OVER BUDGET  {line}")


def cmd_files(a):
    budgets = {}
    for item in a.budget or []:
        name, _, limit = item.partition("=")
        if not limit.isdigit():
            sys.exit(f"token_audit: --budget takes NAME=BYTES, got {item!r}")
        budgets[name] = int(limit)
    repos = a.repos or ["."]
    for repo in repos:
        if not os.path.isdir(repo):
            sys.exit(f"token_audit: {repo}: not a directory")
    audits = [audit_repo(repo, a.bytes_per_token) for repo in repos]
    dups = duplicates(audits) if len(audits) > 1 else []
    over = check_budgets(audits, budgets, a.budget_loaded)
    if a.json:
        print(
            json.dumps(
                {
                    "bytes_per_token": a.bytes_per_token,
                    "repositories": [
                        {k: v for k, v in audit.items() if k != "root"} for audit in audits
                    ],
                    "duplicates": dups,
                    "over_budget": over,
                },
                indent=1,
            )
        )
    else:
        print_files(audits, dups, over, a.bytes_per_token, a.top)
    return 1 if over else 0


# --- transcript -----------------------------------------------------------


def redact(text):
    """A call's input may hold a credential: the value after a key that names
    one, and any long unbroken run that looks like a key, are not printed."""

    def run(m):
        # a key mixes cases and digits, or is long hex; a kebab-case name or a UUID is neither
        v = m.group(0)
        mixed = re.search(r"[a-z]", v) and re.search(r"[A-Z]", v) and re.search(r"\d", v)
        return "[redacted]" if mixed or re.fullmatch(r"[0-9a-fA-F]{32,}", v) else v

    text = SECRET_KEY.sub(lambda m: m.group(1) + "[redacted]", text)
    return SECRET_VALUE.sub(run, text)


def summarize_input(value):
    if not isinstance(value, dict):
        return ""
    for key in ("description", "command", "file_path", "pattern", "query", "url", "prompt"):
        if isinstance(value.get(key), str):
            return redact(" ".join(value[key].split()))[:60]
    parts = [f"{k}={v}" for k, v in value.items() if isinstance(v, (str, int, float, bool))]
    return redact(" ".join(parts))[:60]


def result_bytes(content):
    if isinstance(content, str):
        return size(content)
    total = 0
    for block in content if isinstance(content, list) else []:
        if isinstance(block, dict) and isinstance(block.get("text"), str):
            total += size(block["text"])
        else:
            total += size(json.dumps(block))
    return total


def audit_transcript(path):
    usage, order = {}, []
    calls, results = {}, []
    repeated = collections.Counter()
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                msg = json.loads(line).get("message")
            except (ValueError, AttributeError):
                continue
            if not isinstance(msg, dict):
                continue
            u = msg.get("usage")
            if msg.get("role") == "assistant" and isinstance(u, dict) and msg.get("id"):
                if msg["id"] not in usage:  # one line per content block repeats the usage
                    order.append(msg["id"])
                usage[msg["id"]] = {
                    k: int(u.get(k) or 0)
                    for k in (
                        "input_tokens",
                        "cache_creation_input_tokens",
                        "cache_read_input_tokens",
                        "output_tokens",
                    )
                }
            content = msg.get("content")
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use" and block.get("id") not in calls:
                    calls[block["id"]] = (block.get("name", "?"), block.get("input"))
                    repeated[
                        (block.get("name", "?"), json.dumps(block.get("input"), sort_keys=True))
                    ] += 1
                elif block.get("type") == "tool_result":
                    results.append((block.get("tool_use_id"), result_bytes(block.get("content"))))

    def context(mid):
        u = usage[mid]
        return u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]

    tools = collections.defaultdict(lambda: {"calls": 0, "result_bytes": 0})
    for name, _ in calls.values():
        tools[name]["calls"] += 1
    largest = []
    for call_id, nbytes in results:
        name, value = calls.get(call_id, ("(call not in this file)", None))
        tools[name]["result_bytes"] += nbytes
        largest.append({"tool": name, "bytes": nbytes, "input": summarize_input(value)})
    totals = {
        k: sum(u[k] for u in usage.values())
        for k in (
            "input_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
            "output_tokens",
        )
    }
    return {
        "file": path,
        "requests": len(usage),
        "totals": totals,
        "first_context": context(order[0]) if order else 0,
        "largest_context": max((context(m) for m in order), default=0),
        "tools": {k: v for k, v in sorted(tools.items(), key=lambda kv: -kv[1]["result_bytes"])},
        "largest_results": sorted(largest, key=lambda r: -r["bytes"]),
        "repeated": [
            {"tool": name, "times": n, "input": summarize_input(json.loads(value))}
            for (name, value), n in repeated.most_common()
            if n > 1
        ],
    }


def print_transcript(t, top, min_calls):
    tot = t["totals"]
    print(f"== {t['file']} ==")
    print(
        f"requests: {t['requests']:,}; context of the first request: {t['first_context']:,} "
        f"tokens; largest context: {t['largest_context']:,} tokens (measured)"
    )
    print(
        f"input read: {tot['input_tokens']:,} uncached + {tot['cache_creation_input_tokens']:,} "
        f"written to cache + {tot['cache_read_input_tokens']:,} read from cache; "
        f"output: {tot['output_tokens']:,}"
    )
    all_bytes = sum(v["result_bytes"] for v in t["tools"].values())
    print(
        f"tool results: {all_bytes:,} bytes from "
        f"{sum(v['calls'] for v in t['tools'].values()):,} call(s)"
    )
    for name, v in list(t["tools"].items())[:top]:
        share = 100 * v["result_bytes"] // max(all_bytes, 1)
        print(f"    {v['result_bytes']:>10,} bytes  {share:>2} %  {v['calls']:>4} call(s)  {name}")
    if t["largest_results"]:
        print("  largest results:")
    for r in t["largest_results"][:top]:
        print(f"    {r['bytes']:>10,} bytes  {r['tool']}  {r['input']}")
    for r in t["repeated"][:top]:
        print(f"  repeated {r['times']} times with the same input: {r['tool']}  {r['input']}")
    for name, v in t["tools"].items():
        if v["calls"] >= min_calls:
            print(
                f"  candidate for a script or a data file: {name}, {v['calls']} calls, "
                f"{v['result_bytes']:,} bytes of results"
            )


def cmd_transcript(a):
    audits = []
    for path in a.files:
        if not os.path.isfile(path):
            sys.exit(f"token_audit: {path}: no such file")
        audits.append(audit_transcript(path))
    if a.json:
        print(json.dumps(audits, indent=1))
        return 0
    for t in audits:
        print_transcript(t, a.top, a.min_calls)
    if len(audits) > 1:
        keys = (
            "input_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
            "output_tokens",
        )
        s = {k: sum(t["totals"][k] for t in audits) for k in keys}
        print(f"== all {len(audits)} transcripts ==")
        print(
            f"requests: {sum(t['requests'] for t in audits):,}; input read: "
            f"{s['input_tokens'] + s['cache_creation_input_tokens'] + s['cache_read_input_tokens']:,}"
            f" tokens ({s['cache_read_input_tokens']:,} from cache); output: "
            f"{s['output_tokens']:,}"
        )
    return 0


# --- self-test ------------------------------------------------------------


def self_test():
    failures = []

    def check(what, ok):
        print(f"{'ok  ' if ok else 'FAIL'}  {what}")
        if not ok:
            failures.append(what)

    managed = (
        "<!-- org-sync:begin org-rules -->\n"
        + "The same rule in every repository.\n" * 8
        + "<!-- org-sync:end org-rules -->\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        for name, extra in (("one", "Status 2026-11-12: part done (#7, #8).\n"), ("two", "")):
            repo = os.path.join(tmp, name)
            os.makedirs(os.path.join(repo, ".claude", "skills", "demo"))
            os.makedirs(os.path.join(repo, "docs"))
            with open(os.path.join(repo, "CLAUDE.md"), "w", encoding="utf-8") as f:
                f.write(
                    "# CLAUDE.md\n\n@AGENTS.md\n\n```\n@docs/not-an-import.md\n```\n"
                    "See `user@example.com`.\n"
                )
            with open(os.path.join(repo, "AGENTS.md"), "w", encoding="utf-8") as f:
                f.write(
                    f"# AGENTS.md\n\n## What this repo is\n\n{extra}Layout of {name}.\n\n"
                    f"## Golden rules\n\n{managed}\n## Where to look\n\n"
                    "[the guide](docs/guide.md) and `docs/missing.md`\n"
                )
            with open(os.path.join(repo, "docs", "guide.md"), "w", encoding="utf-8") as f:
                f.write("x" * 5000)
            with open(os.path.join(repo, "docs", "not-an-import.md"), "w", encoding="utf-8") as f:
                f.write("y" * 100)
            with open(
                os.path.join(repo, ".claude", "skills", "demo", "SKILL.md"), "w", encoding="utf-8"
            ) as f:
                f.write(
                    "---\nname: demo\ndescription: A demo skill.\nlicense: MIT\n---\n"
                    + "body\n" * 50
                )
        one, two = (audit_repo(os.path.join(tmp, n), BYTES_PER_TOKEN) for n in ("one", "two"))
        paths = [f["path"] for f in one["files"]]
        check(
            "CLAUDE.md is the entry and its @AGENTS.md import is loaded",
            paths == ["CLAUDE.md", "AGENTS.md"],
        )
        check("an @path in a code block or an e-mail address is no import", len(paths) == 2)
        claude, agents = one["files"]
        check(
            "a file's bytes are its size on disk",
            agents["bytes"] == os.path.getsize(os.path.join(tmp, "one", "AGENTS.md")),
        )
        titles = [s["title"] for s in agents["sections"]]
        check(
            "sections split at the ## headings",
            titles == ["(top)", "## What this repo is", "## Golden rules", "## Where to look"],
        )
        check(
            "section bytes add up to the file",
            sum(s["bytes"] for s in agents["sections"]) == agents["bytes"],
        )
        rules = agents["sections"][2]
        check(
            "the org-sync block is counted as managed, markers included",
            rules["managed"] == {"org-rules": size(managed)},
        )
        spanning = sections(
            "intro\n<!-- org-sync:begin org -->\n## One\n\ntext\n## Two\n\ntext\n"
            "<!-- org-sync:end org -->\n## Three\n\nown text\n"
        )
        check(
            "a block that starts before a heading and spans two sections is managed in both",
            [sorted(s["managed"]) for s in spanning] == [["org"], ["org"], ["org"], []]
            and sum(sum(s["managed"].values()) for s in spanning)
            == size(
                "<!-- org-sync:begin org -->\n## One\n\ntext\n## Two\n\ntext\n"
                "<!-- org-sync:end org -->\n"
            ),
        )
        what = agents["sections"][1]
        check(
            "dates and issue numbers in a section are counted",
            (what["dates"], what["issues"]) == (1, 2),
        )
        check(
            "a skill's name and description are listed, its body is not",
            one["skills"][0]["listed_bytes"] == size("name: demo\ndescription: A demo skill.")
            and one["skills_listed_bytes"] < one["skills"][0]["body_bytes"],
        )
        check(
            "loaded bytes are the files plus the skill listing",
            one["loaded_bytes"] == claude["bytes"] + agents["bytes"] + one["skills_listed_bytes"],
        )
        check(
            "a linked file that exists is read on demand; a missing one is ignored",
            one["on_demand"] == [{"path": "docs/guide.md", "bytes": 5000}],
        )
        dups = duplicates([one, two])
        check(
            "the section that is the same in both repositories is found once",
            [d["title"] for d in dups] == ["## Golden rules"]
            and dups[0]["repeated_bytes"] == rules["bytes"],
        )
        check(
            "a short identical section is not worth reporting",
            "## Where to look" not in [d["title"] for d in dups],
        )
        check(
            "a section that differs is not a duplicate",
            "## What this repo is" not in [d["title"] for d in dups],
        )
        check(
            "a file over its budget is reported",
            len(check_budgets([one], {"AGENTS.md": 10}, None)) == 1,
        )
        check(
            "a file within its budget is not",
            check_budgets([one], {"AGENTS.md": 10**6}, None) == [],
        )
        check(
            "the loaded total has its own budget",
            len(check_budgets([one, two], {}, two["loaded_bytes"] - 1)) == 2,
        )
        ns = argparse.Namespace(
            repos=[os.path.join(tmp, "one")],
            budget=["AGENTS.md=10"],
            budget_loaded=None,
            bytes_per_token=BYTES_PER_TOKEN,
            top=3,
            json=True,
        )
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            code = cmd_files(ns)
        check(
            "--json prints one JSON document", json.loads(printed.getvalue())["over_budget"] != []
        )
        check("files exits 1 over budget", code == 1)
        bare = os.path.join(tmp, "bare")
        os.makedirs(bare)
        with open(os.path.join(bare, "AGENTS.md"), "w", encoding="utf-8") as f:
            f.write("# AGENTS.md\n")
        check(
            "AGENTS.md alone is the entry where there is no CLAUDE.md",
            loaded_files(bare) == [("AGENTS.md", "entry (no CLAUDE.md)")],
        )
        check("tokens are bytes over the ratio, rounded up", tokens(8, 3.5) == 3)

        usage = {
            "input_tokens": 10,
            "cache_creation_input_tokens": 1000,
            "cache_read_input_tokens": 0,
            "output_tokens": 50,
        }
        later = dict(usage, cache_creation_input_tokens=200, cache_read_input_tokens=1010)
        lines = [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "id": "m1",
                    "usage": usage,
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "t1",
                            "name": "Bash",
                            "input": {"command": "ls", "description": "List files"},
                        }
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "id": "m1",
                    "usage": usage,
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "t2",
                            "name": "issue_read",
                            "input": {"repo": "x", "issue_number": 1},
                        }
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "t1", "content": "a" * 100},
                        {
                            "type": "tool_result",
                            "tool_use_id": "t2",
                            "content": [{"type": "text", "text": "b" * 3000}],
                        },
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "id": "m2",
                    "usage": later,
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "t3",
                            "name": "Bash",
                            "input": {"command": "ls", "description": "List files"},
                        }
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": "t3", "content": "a" * 100}],
                },
            },
            {"type": "attachment"},
        ]
        log = os.path.join(tmp, "session.jsonl")
        with open(log, "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(line) for line in lines) + "\nnot json\n")
        t = audit_transcript(log)
        check("a message written on two lines is one request", t["requests"] == 2)
        check("the first request's context is its three input counts", t["first_context"] == 1010)
        check("the largest context is found", t["largest_context"] == 1220)
        check(
            "totals add each request once",
            t["totals"]["output_tokens"] == 100 and t["totals"]["cache_read_input_tokens"] == 1010,
        )
        check(
            "results are added per tool, largest first",
            list(t["tools"].items())
            == [
                ("issue_read", {"calls": 1, "result_bytes": 3000}),
                ("Bash", {"calls": 2, "result_bytes": 200}),
            ],
        )
        check(
            "the largest result names its tool and input",
            t["largest_results"][0]
            == {"tool": "issue_read", "bytes": 3000, "input": "repo=x issue_number=1"},
        )
        check(
            "a call repeated with the same input is reported",
            t["repeated"] == [{"tool": "Bash", "times": 2, "input": "List files"}],
        )
    with tempfile.TemporaryDirectory() as tmp:

        def write(rel, text):
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)

        outside = os.path.join(tmp, "outside.md")
        write("outside.md", "not in the repository\n")
        for name in ("a/repo", "b/repo"):
            write(f"{name}/CLAUDE.md", "# CLAUDE.md\r\n\r\n@docs/out.md\r\n\r\n## Rules\r\ntext")
            write(
                f"{name}/AGENTS.md",
                "# Not imported\n\n````\n~~~\n## In a code block\n@docs/guide.md\n````\n\n"
                "## Shared\n" + "The same text in both.\n" * 12,
            )
            write(
                f"{name}/skills/demo/SKILL.md",
                "---\nname: demo\ndescription: >-\n  Text on the lines\n  below the key.\n"
                "license: MIT\n---\n\nBody.\n",
            )
            os.makedirs(os.path.join(tmp, name, "docs"))
            os.symlink(outside, os.path.join(tmp, name, "docs", "out.md"))
        a, b = (audit_repo(os.path.join(tmp, n), BYTES_PER_TOKEN) for n in ("a/repo", "b/repo"))
        claude = a["files"][0]
        check(
            "an import that is a symlink out of the repository is not followed",
            [f["path"] for f in a["files"]] == ["CLAUDE.md"],
        )
        check(
            "a file with CRLF line endings has its size on disk",
            claude["bytes"] == os.path.getsize(os.path.join(tmp, "a/repo/CLAUDE.md")),
        )
        check(
            "the sections of a file add up to the file, with no final newline too",
            sum(s["bytes"] for s in claude["sections"]) == claude["bytes"],
        )
        text = read(os.path.join(tmp, "a/repo/AGENTS.md"))
        check(
            "a fence closes only on its own character, at least as long",
            [s["title"] for s in sections(text)] == ["(top)", "## Shared"] and imports(text) == [],
        )
        check(
            "a description written as a block scalar is listed with its text",
            a["skills"][0]["listed_bytes"]
            == size("name: demo\ndescription: >-\n  Text on the lines\n  below the key."),
        )
        write("a/repo/CLAUDE.md", "# CLAUDE.md\n\n@AGENTS.md\n")
        write("b/repo/CLAUDE.md", "# CLAUDE.md\n\n@AGENTS.md\n")
        a, b = (audit_repo(os.path.join(tmp, n), BYTES_PER_TOKEN) for n in ("a/repo", "b/repo"))
        check(
            "two repositories with the same directory name are still two",
            [d["repos"] for d in duplicates([a, b])] == [["repo", "repo"]],
        )
        write("a/repo/CLAUDE.md", "# CLAUDE.md\n")
        a = audit_repo(os.path.join(tmp, "a/repo"), BYTES_PER_TOKEN)
        check(
            "a named file has its budget when no session loads it",
            len(check_budgets([a], {"AGENTS.md": 10}, None)) == 1
            and check_budgets([a], {"AGENTS.md": 10**6, "MISSING.md": 1}, None) == [],
        )
    check(
        "a credential in a call's input is not printed",
        summarize_input({"command": "curl -H 'Authorization: Bearer abc' https://x"})
        == "curl -H 'Authorization: [redacted] abc' https://x"
        and summarize_input({"command": "export API_KEY=hunter2 && run"})
        == "export API_KEY=[redacted] && run"
        and "ghp_"
        not in summarize_input({"command": "git push ghp_0123456789abcdefghijABCDEFGHIJ"})
        and summarize_input({"file_path": "/home/user/skills/tools/token-audit/token_audit.py"})
        == "/home/user/skills/tools/token-audit/token_audit.py"
        and summarize_input(
            {
                "file_path": "/tmp/c2d8a7ce-2fd7-5e19-b61c-a5ef15fae6ec/a-long-kebab-case-directory-name"
            }
        )
        == "/tmp/c2d8a7ce-2fd7-5e19-b61c-a5ef15fae6ec/a-long-kebab-case-",
    )
    check(
        "long hex is taken for a key",
        summarize_input({"command": "use 0123456789abcdef0123456789abcdef now"})
        == "use [redacted] now",
    )
    print(f"token_audit self-test: {'FAILED' if failures else 'OK'}")
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    f = sub.add_parser("files", help="what a session loads before its first tool call")
    f.add_argument("repos", nargs="*", metavar="REPO")
    f.add_argument("--budget", action="append", metavar="NAME=BYTES")
    f.add_argument("--budget-loaded", type=int, metavar="BYTES")
    f.add_argument("--bytes-per-token", type=float, default=BYTES_PER_TOKEN)
    f.add_argument("--top", type=int, default=8)
    f.add_argument("--json", action="store_true")
    t = sub.add_parser("transcript", help="where a finished session's tokens went")
    t.add_argument("files", nargs="+", metavar="FILE")
    t.add_argument("--min-calls", type=int, default=20)
    t.add_argument("--top", type=int, default=8)
    t.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.cmd == "files":
        if a.bytes_per_token <= 0:
            ap.error("--bytes-per-token must be positive")
        return cmd_files(a)
    if a.cmd == "transcript":
        return cmd_transcript(a)
    ap.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
