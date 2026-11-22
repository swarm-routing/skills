#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""swarm-mcp: a local, read-only MCP server over the org's scripts (ADR-0002, #185).

Each tool runs one read-only command of a swarm-routing/.github script through
the skill wrapper that already finds it (`skills/<skill>/scripts/`:
ORG_TOOLS_DIR, else a cached snapshot of swarm-routing/.github at
ORG_TOOLS_REF, default main) and returns the exit status and the script's
summary, trimmed to a size cap. The server itself opens no connection, reads
no token and writes no file; a script reaches the network only as it does
when a person runs it (git, gh, public HTTPS reads).

Transport: JSON-RPC 2.0 over stdio, one message per line. Dual-era: a modern
request (protocol 2026-07-28) carries its version in
`params._meta["io.modelcontextprotocol/protocolVersion"]`; a legacy client
opens with `initialize` (2025-11-25, 2025-06-18, 2025-03-26).

  python3 -I tools/swarm-mcp/swarm_mcp.py            serve on stdin/stdout
  python3 -I tools/swarm-mcp/swarm_mcp.py --list     print the tools, one per line
  python3 -I tools/swarm-mcp/swarm_mcp.py --self-test

Environment:
  CLAUDE_PROJECT_DIR   the directory relative paths resolve against (else the cwd)
  ORG_TOOLS_DIR        a swarm-routing/.github checkout (the wrappers read it)
  SWARM_MCP_TIMEOUT    seconds per tool call (default 300)
  SWARM_MCP_MAX_CHARS  characters of stdout per result (default 6000; stderr gets a quarter)

Stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile

NAME = "swarm-mcp"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MODERN = ["2026-07-28"]
LEGACY = ["2025-11-25", "2025-06-18", "2025-03-26"]
SUPPORTED = MODERN + LEGACY
META_VERSION = "io.modelcontextprotocol/protocolVersion"
UNSUPPORTED_VERSION = -32022
INSTRUCTIONS = (
    "Read-only verdicts from the swarm-routing org's scripts: a fidelity sheet's check, row and "
    "locator verification, the golden-rule checks on a diff, a release's readiness and aftercare, "
    "a release lock's state. Each result is the script's own summary; exit 1 means findings."
)


def server_version():
    try:
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("version", "0")
    except (OSError, ValueError):
        return "0"


# --- the tools -----------------------------------------------------------------------

SEMVER = r"^v?\d+\.\d+\.\d+$"
TAG = r"^v\d+\.\d+\.\d+$"
REPO = r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9._-]+$"
REF = r"^[A-Za-z0-9][A-Za-z0-9._/@~^-]*$"
TEXT = r"^[A-Za-z0-9_-]+=.+$"


def _s(desc, pattern=None):
    d = {"type": "string", "description": desc}
    if pattern:
        d["pattern"] = pattern
    return d


def _schema(props, required=()):
    return {
        "type": "object",
        "properties": props,
        "required": list(required),
        "additionalProperties": False,
    }


FIDELITY = ("fidelity-sheet", "fidelity")
REVIEW = ("protocol-review", "check-invariants")
RELEASE = ("release", "org-tool", "release-check")
LOCK = ("dependency-bump", "org-tool", "release-lock")

# name -> (description, input schema, wrapper, argv builder); listed in this order
TOOLS = {
    "fidelity_check": (
        "fidelity.py check: a fidelity sheet's shape and Source cells (a reference, a reasoned "
        "repo choice, or unknown), listing the unknowns and repo choices. Exit 1 on a problem.",
        _schema({"file": _s("the sheet, e.g. docs/fidelity.md")}, ["file"]),
        FIDELITY,
        lambda a: ["check", a["file"]],
    ),
    "fidelity_row": (
        "fidelity.py row: the sheet's one-line summary row (the review table's shape).",
        _schema(
            {
                "file": _s("the sheet, e.g. docs/fidelity.md"),
                "protocol": _s("the protocol's name; default: the sheet's H1"),
            },
            ["file"],
        ),
        FIDELITY,
        lambda a: ["row", a["file"]] + (["--protocol", a["protocol"]] if a.get("protocol") else []),
    ),
    "fidelity_verify": (
        "fidelity.py verify: each [KEY] locator of the sheet against the source's extracted text "
        "(the place exists; a Table N row's value is in that table). Exit 1 on a miss.",
        _schema(
            {
                "file": _s("the sheet, e.g. docs/fidelity.md"),
                "texts": {
                    "type": "array",
                    "minItems": 1,
                    "items": _s("KEY=PATH: a source key and its extracted text file", TEXT),
                    "description": "one KEY=PATH per source key",
                },
            },
            ["file", "texts"],
        ),
        FIDELITY,
        lambda a: ["verify", a["file"]] + [x for t in a["texts"] for x in ("--text", t)],
    ),
    "protocol_review": (
        "check_invariants.py: the org golden rules' mechanical checks on a repository's diff "
        "against a base. Exit 1 on a finding.",
        _schema(
            {
                "repo": _s("the repository checkout (default .)"),
                "base": _s("the base ref (default origin/main)", REF),
                "pr_body": _s("a file holding the PR text, for the rule 6 claims"),
            }
        ),
        REVIEW,
        lambda a: (
            [a.get("repo", "."), "--base", a.get("base", "origin/main")]
            + (["--pr-body", a["pr_body"]] if a.get("pr_body") else [])
        ),
    ),
    "release_ready": (
        "release_check.py ready: is a repository ready for a release dry-run or bump (caller "
        "workflow, Commitizen, make dist, the ladder row, open release issues). One OK/WARN/FAIL/"
        "NEXT line per check; exit 1 on a FAIL.",
        _schema(
            {
                "repo_dir": _s("the repository checkout"),
                "repo": _s("OWNER/NAME, for the issue scope and the bump PR", REPO),
                "version": _s("the version the dry-run computed, X.Y.Z", SEMVER),
            },
            ["repo_dir"],
        ),
        RELEASE,
        lambda a: (
            ["ready", a["repo_dir"]]
            + (["--repo", a["repo"]] if a.get("repo") else [])
            + (["--version", a["version"]] if a.get("version") else [])
        ),
    ),
    "release_after": (
        "release_check.py after: did everything follow a release (tag, assets, Zenodo, the site, "
        "consumers' locks). One line per check; exit 1 on a FAIL.",
        _schema(
            {
                "repo": _s("OWNER/NAME", REPO),
                "tag": _s("vX.Y.Z", TAG),
                "repos": _s(
                    "the consumers to look at, comma-separated (default: every public one)"
                ),
            },
            ["repo", "tag"],
        ),
        RELEASE,
        lambda a: (
            ["after", a["repo"], "--tag", a["tag"]]
            + (["--repos", a["repos"]] if a.get("repos") else [])
        ),
    ),
    "lock_verify": (
        "release_lock.py verify: a release lock (swarm-core.lock, ns3-tools.lock) against its "
        "release: the tag's commit, the version, each asset's SHA256. Exit 1 on a mismatch.",
        _schema({"lock": _s("the lock file, e.g. swarm-core.lock")}, ["lock"]),
        LOCK,
        lambda a: ["verify", a["lock"]],
    ),
}


def tool_list():
    return [
        {"name": n, "description": d, "inputSchema": s, "annotations": {"readOnlyHint": True}}
        for n, (d, s, _w, _b) in TOOLS.items()
    ]


def validate(schema, args):
    """The schema subset the tools use; a list of problems."""
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    errs = []
    props = schema["properties"]
    for k in schema["required"]:
        if k not in args:
            errs.append(f"missing `{k}`")
    for k, v in args.items():
        if k not in props:
            errs.append(f"unknown argument `{k}`")
            continue
        p = props[k]
        vals = v if p["type"] == "array" else [v]
        if p["type"] == "array":
            if not isinstance(v, list) or len(v) < p.get("minItems", 0):
                errs.append(f"`{k}` must be a list of at least {p.get('minItems', 0)}")
                continue
            p = p["items"]
        for x in vals:
            if not isinstance(x, str) or not x or "\0" in x:
                errs.append(f"`{k}` must be a non-empty string")
            elif x.startswith("-"):
                errs.append(f"`{k}` must not start with '-' (no options through arguments)")
            elif "pattern" in p and not re.match(p["pattern"], x):
                errs.append(f"`{k}` must match {p['pattern']}")
    return errs


def trim(text, cap):
    if len(text) <= cap:
        return text
    head, tail = cap * 2 // 3, cap // 3
    cut = len(text) - head - tail
    return (
        f"{text[:head]}\n[... {cut} characters cut by swarm-mcp; run the script for the full "
        f"output ...]\n{text[-tail:]}"
    )


def run(name, args, env=None):
    """(text, is_error) for one tool call."""
    _d, schema, wrapper, build = TOOLS[name]
    problems = validate(schema, args)
    if problems:
        return f"{name}: invalid arguments: " + "; ".join(problems), True
    env = dict(os.environ if env is None else env)
    cwd = env.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    timeout = float(env.get("SWARM_MCP_TIMEOUT", "300"))
    cap = int(env.get("SWARM_MCP_MAX_CHARS", "6000"))
    skill, script, *sub = wrapper
    cmd = [os.path.join(ROOT, "skills", skill, "scripts", script), *sub, *build(args)]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            start_new_session=True,
        )
    except OSError as e:
        return f"{name}: could not start {cmd[0]}: {e}", True
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        return f"{name}: timed out after {timeout:g} s\n{trim(err, cap // 4)}".rstrip(), True
    code = proc.returncode
    verdict = {0: "ok", 1: "findings"}.get(code, "error")
    text = f"{name}: exit {code} ({verdict})\n{trim(out, cap)}".rstrip()
    if err.strip():
        text += f"\n--- stderr ---\n{trim(err, cap // 4)}".rstrip()
    return text, code not in (0, 1)


# --- JSON-RPC ------------------------------------------------------------------------


def _err(mid, code, message, data=None):
    e = {"code": code, "message": message}
    if data is not None:
        e["data"] = data
    return {"jsonrpc": "2.0", "id": mid, "error": e}


def handle(msg, state):
    """One reply for one message (None for a notification)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return _err(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
    if "id" not in msg:
        return None  # notifications/initialized, cancellations: nothing to answer
    mid, method = msg["id"], msg["method"]
    params = msg.get("params") or {}
    if not isinstance(params, dict):
        return _err(mid, -32602, "params must be an object")
    meta = params.get("_meta") if isinstance(params.get("_meta"), dict) else {}
    info = {"name": NAME, "version": server_version()}
    caps = {"tools": {}}

    if method == "initialize":
        asked = params.get("protocolVersion")
        state["legacy"] = asked if asked in LEGACY else LEGACY[0]
        result = {
            "protocolVersion": state["legacy"],
            "capabilities": caps,
            "serverInfo": info,
            "instructions": INSTRUCTIONS,
        }
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    version = meta.get(META_VERSION)
    if version is not None and version not in SUPPORTED:
        return _err(
            mid,
            UNSUPPORTED_VERSION,
            "Unsupported protocol version",
            {"supported": SUPPORTED, "requested": version},
        )
    modern = version in MODERN

    if method == "server/discover":
        result = {
            "supportedVersions": SUPPORTED,
            "capabilities": caps,
            "_meta": {"io.modelcontextprotocol/serverInfo": info},
            "instructions": INSTRUCTIONS,
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": tool_list()}
    elif method == "tools/call":
        name = params.get("name")
        if name not in TOOLS:
            return _err(mid, -32602, f"Unknown tool: {name}")
        text, is_error = run(name, params.get("arguments") or {})
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
    else:
        return _err(mid, -32601, f"Method not found: {method}")
    if modern:
        result = {"resultType": "complete", **result}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve(inp=sys.stdin, out=sys.stdout):
    state = {}
    for line in inp:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply = _err(None, -32700, "Parse error")
        else:
            reply = handle(msg, state)
        if reply is not None:
            out.write(json.dumps(reply, separators=(",", ":")) + "\n")
            out.flush()
    return 0


# --- self-test -----------------------------------------------------------------------

# One fake for every org script: it prints its argv, and its arguments steer it.
FAKE = """import json, sys, time
a = sys.argv[1:]
print("ARGV " + json.dumps(a))
if any("sleep" in x for x in a):
    time.sleep(30)
if any("big" in x for x in a):
    print("x" * 50000 + " TAIL")
if any("warn" in x for x in a):
    print("a warning", file=sys.stderr)
sys.exit(2 if any("fail2" in x for x in a) else 1 if any("fail1" in x for x in a) else 0)
"""


def self_test():
    failures = []

    def check(cond, what):
        print(f"{'ok' if cond else 'FAIL':5} {what}")
        if not cond:
            failures.append(what)

    org = tempfile.mkdtemp(prefix="swarm-mcp-org-")
    for rel in (
        "tools/fidelity/fidelity.py",
        "tools/protocol-review/check_invariants.py",
        "tools/release/release_check.py",
        "tools/checks/release_lock.py",
    ):
        os.makedirs(os.path.join(org, os.path.dirname(rel)), exist_ok=True)
        with open(os.path.join(org, rel), "w", encoding="utf-8") as f:
            f.write(FAKE)
    project = tempfile.mkdtemp(prefix="swarm-mcp-project-")
    env = dict(os.environ)
    env.pop("ORG_TOOLS_REF", None)
    env.update(
        ORG_TOOLS_DIR=org,
        CLAUDE_PROJECT_DIR=project,
        SWARM_MCP_TIMEOUT="2",
        SWARM_MCP_MAX_CHARS="1200",
    )
    modern = {META_VERSION: MODERN[0], "io.modelcontextprotocol/clientInfo": {"name": "t"}}

    def req(i, method, params=None):
        m = {"jsonrpc": "2.0", "id": i, "method": method}
        if params is not None:
            m["params"] = params
        return json.dumps(m)

    def call(i, name, args, meta=None):
        p = {"name": name, "arguments": args}
        if meta:
            p["_meta"] = meta
        return req(i, "tools/call", p)

    lines = [
        req(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        req(2, "tools/list"),
        call(3, "fidelity_check", {"file": "docs/fidelity.md"}),
        call(4, "fidelity_verify", {"file": "f.md", "texts": ["G02=/t/g.txt", "W05=w.txt"]}),
        call(5, "protocol_review", {}),
        call(
            6, "release_ready", {"repo_dir": ".", "repo": "swarm-routing/ARA", "version": "0.3.0"}
        ),
        call(7, "release_after", {"repo": "swarm-routing/ARA", "tag": "v0.3.0"}),
        call(8, "lock_verify", {"lock": "swarm-core.lock"}),
        call(9, "fidelity_check", {"file": "fail1.md"}),
        call(10, "fidelity_check", {"file": "fail2-warn.md"}),
        call(11, "fidelity_check", {"file": "sleep.md"}),
        call(12, "fidelity_check", {"file": "big.md"}),
        call(13, "fidelity_check", {}),
        call(14, "fidelity_check", {"file": "--self-test"}),
        call(15, "release_ready", {"repo_dir": ".", "version": "1.2"}),
        call(16, "lock_verify", {"lock": "x.lock", "base": "file:///"}),
        call(17, "no_such_tool", {}),
        req(18, "resources/list"),
        "{not json",
        req(19, "server/discover", {"_meta": modern}),
        call(20, "fidelity_row", {"file": "f.md", "protocol": "ARA"}, modern),
        req(21, "tools/list", {"_meta": {META_VERSION: "1900-01-01"}}),
        req(22, "ping"),
        json.dumps([1, 2]),
    ]
    proc = subprocess.run(
        [sys.executable, "-I", os.path.abspath(__file__)],
        input="\n".join(lines) + "\n",
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    replies = [json.loads(x) for x in proc.stdout.splitlines()]
    by_id = {r.get("id"): r for r in replies}
    res = {i: r.get("result", {}) for i, r in by_id.items()}

    def text(i):
        c = res.get(i, {}).get("content") or [{}]
        return c[0].get("text", "")

    check(proc.returncode == 0, "the server exits 0 at the end of its input")
    check(len(replies) == 24, f"one reply per request, none for the notification ({len(replies)})")
    init = res.get(1, {})
    check(
        init.get("protocolVersion") == "2025-06-18"
        and init.get("serverInfo", {}).get("name") == NAME
        and "tools" in init.get("capabilities", {}),
        "initialize: the legacy version asked for, serverInfo, the tools capability",
    )
    names = [t["name"] for t in res.get(2, {}).get("tools", [])]
    check(names == list(TOOLS), f"tools/list: every tool in a fixed order ({names})")
    check(
        all(t["inputSchema"]["additionalProperties"] is False for t in res[2]["tools"]),
        "tools/list: every schema closes its arguments",
    )
    check("resultType" not in res[2], "a legacy result carries no resultType")
    check(
        text(3).startswith("fidelity_check: exit 0 (ok)")
        and 'ARGV ["check", "docs/fidelity.md"]' in text(3)
        and res[3]["isError"] is False,
        "fidelity_check: the wrapper runs fidelity.py check FILE",
    )
    check(
        'ARGV ["verify", "f.md", "--text", "G02=/t/g.txt", "--text", "W05=w.txt"]' in text(4),
        "fidelity_verify: one --text per KEY=PATH",
    )
    check(
        'ARGV [".", "--base", "origin/main"]' in text(5),
        "protocol_review: defaults . and origin/main",
    )
    check(
        'ARGV ["ready", ".", "--repo", "swarm-routing/ARA", "--version", "0.3.0"]' in text(6),
        "release_ready: ready REPO_DIR --repo --version",
    )
    check(
        'ARGV ["after", "swarm-routing/ARA", "--tag", "v0.3.0"]' in text(7),
        "release_after: after OWNER/NAME --tag",
    )
    check(
        'ARGV ["verify", "swarm-core.lock"]' in text(8), "lock_verify: release_lock.py verify LOCK"
    )
    check(
        "exit 1 (findings)" in text(9) and res[9]["isError"] is False,
        "exit 1 is a verdict with findings, not a tool error",
    )
    check(
        "exit 2 (error)" in text(10)
        and "--- stderr ---\na warning" in text(10)
        and res[10]["isError"],
        "exit 2 is a tool error, and stderr follows the output",
    )
    check(
        "timed out after 2 s" in text(11) and res[11]["isError"],
        "a call past the timeout is killed",
    )
    check(
        "characters cut by swarm-mcp" in text(12)
        and text(12).endswith("TAIL")
        and len(text(12)) < 1400,
        f"the output is capped, head and tail kept ({len(text(12))} chars)",
    )
    check("missing `file`" in text(13) and res[13]["isError"], "a missing argument is a tool error")
    check("must not start with '-'" in text(14), "an argument cannot pass an option to the script")
    check("must match" in text(15), "a version must be X.Y.Z")
    check("unknown argument `base`" in text(16), "an argument outside the schema is refused")
    check(by_id.get(17, {}).get("error", {}).get("code") == -32602, "an unknown tool is -32602")
    check(by_id.get(18, {}).get("error", {}).get("code") == -32601, "an unknown method is -32601")
    check(any(r.get("error", {}).get("code") == -32700 for r in replies), "bad JSON is -32700")
    disc = res.get(19, {})
    check(
        disc.get("resultType") == "complete"
        and disc.get("supportedVersions") == SUPPORTED
        and disc.get("_meta", {}).get("io.modelcontextprotocol/serverInfo", {}).get("name") == NAME,
        "server/discover: the versions, the capabilities, serverInfo in _meta",
    )
    check(
        res.get(20, {}).get("resultType") == "complete"
        and 'ARGV ["row", "f.md", "--protocol", "ARA"]' in text(20),
        "a modern tools/call is served statelessly, with resultType",
    )
    e21 = by_id.get(21, {}).get("error", {})
    check(
        e21.get("code") == UNSUPPORTED_VERSION
        and e21.get("data", {}).get("supported") == SUPPORTED,
        "an unknown protocol version is UnsupportedProtocolVersionError with the supported list",
    )
    check(res.get(22) == {}, "ping answers {}")
    check(
        any(r.get("error", {}).get("code") == -32600 for r in replies),
        "a batch is an invalid request (MCP has no batches)",
    )
    print(f"swarm_mcp self-test: {'ok' if not failures else f'{len(failures)} failed'}")
    return 1 if failures else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--list"]:
        for t in tool_list():
            print(f"{t['name']}: {t['description']}")
        return 0
    if argv:
        print(__doc__, file=sys.stderr)
        return 2
    return serve()


if __name__ == "__main__":
    sys.exit(main())
