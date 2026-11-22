#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Self-test for check-plugins.py: this repo passes; each broken copy fails
with the expected message."""

import importlib.util
import json
import os
import re
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("cp", os.path.join(HERE, "check-plugins.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

assert cp.check(ROOT) == [], cp.check(ROOT)
print("ok    this repo's marketplace is valid")


with open(os.path.join(ROOT, ".claude-plugin/plugin.json")) as fh:
    VERSION = json.load(fh)["version"]


def broken(path, old, new, expect):
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills", "agents"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    for f in (".cz.toml", "CITATION.cff"):
        shutil.copy(os.path.join(ROOT, f), d)
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
    "skills/org-repo/SKILL.md",
    'description: "',
    "description: ",
    "which YAML misreads; quote it",
)
broken(
    ".claude-plugin/plugin.json",
    f'"version": "{VERSION}"',
    '"version": "9.9.9"',
    f"version 9.9.9 != marketplace {VERSION}",
)
broken(
    ".cz.toml",
    f'version = "{VERSION}"',
    'version = "9.9.9"',
    f".cz.toml: version 9.9.9 != plugin.json {VERSION}",
)
broken(
    "CITATION.cff",
    f'version: "{VERSION}"',
    'version: "9.9.9"',
    f"CITATION.cff: version 9.9.9 != plugin.json {VERSION}",
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
broken(
    "skills/docs-review/evals/orphan-docs-page/graders/02.md",
    "type: llm",
    "type: script",
    "grader `type` is `script`",
)
broken(
    "skills/docs-review/evals/orphan-docs-page/graders/05.sh",
    "# grader: check_docs.py",
    "# check_docs.py",
    "no `# grader: <criterion>` line",
)
broken("agents/org-worker.md", "name: org-worker", "name: worker", "!= file name `org-worker`")
broken(
    "agents/org-worker.md",
    "omitClaudeMd: true",
    "omitClaudeMd: true\npermissionMode: bypassPermissions",
    "`permissionMode` is ignored for plugin agents",
)
broken(
    "agents/org-worker.md",
    "omitClaudeMd: true",
    "omitClaudeMd: true\nomitAgentsMd: true",
    "field `omitAgentsMd` is not a subagent field",
)
broken("agents/org-worker.md", "omitClaudeMd: true", "omitClaudeMd: yes", "must be true or false")
broken(
    "agents/org-worker.md",
    "omitClaudeMd: true",
    "omitClaudeMd: true\nskills: org-repo, nope",
    "preloaded skill `nope` is not in the plugin",
)


def grader_files():
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    g = os.path.join(d, "skills/docs-review/evals/orphan-docs-page/graders")
    os.chmod(os.path.join(g, "05.sh"), 0o644)
    open(os.path.join(g, "06.py"), "w").write("print(1)\n")
    errs = cp.check(d)
    assert any("05.sh: not executable" in e for e in errs), errs
    assert any("06.py: a grader is an .md" in e for e in errs), errs
    print("ok    a script grader must be executable; other grader files are rejected")


grader_files()


def orphan():
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    os.makedirs(os.path.join(d, "elsewhere"))
    shutil.move(os.path.join(d, "skills", "fidelity-sheet"), os.path.join(d, "elsewhere"))
    shutil.copytree(
        os.path.join(d, "elsewhere", "fidelity-sheet"),
        os.path.join(d, "skills", "ns3--bad"),
    )
    errs = cp.check(d)
    assert any("ns3--bad" in e and "single hyphens" in e for e in errs), errs
    print("ok    a doubled hyphen in a skill name is rejected")


orphan()

broken(
    "skills/lit-search/scripts/lit-search",
    "flock -w 600 9",
    "flock -w 60 9",
    "lit-search: cached-checkout block differs from",
)
broken(
    "skills/org-repo/scripts/org-sync",
    "exec python3 -I",
    'git -C "$dir" fetch -q origin main\nexec python3 -I',
    "org-sync: fetches or caches outside the cached-checkout block",
)


def no_block():
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    p = os.path.join(d, "skills/fidelity-sheet/scripts/fidelity")
    text = open(p).read()
    open(p, "w").write(cp.BLOCK.sub("", text))
    errs = cp.check(d)
    assert any("fidelity: calls cached_checkout but carries no" in e for e in errs), errs
    print("ok    a wrapper calling cached_checkout without the block is rejected")


no_block()


def mcp(servers, expect):
    """A copy whose .mcp.json is `servers` (a dict, or raw text) fails with `expect`,
    or passes when `expect` is None. Beside the copy is an outside.py, so a path
    that leaves the plugin names a file that exists."""
    top = tempfile.mkdtemp()
    open(os.path.join(top, "outside.py"), "w").write("print(1)\n")
    d = os.path.join(top, "plugin")
    for sub in (".claude-plugin", "skills", "tools"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    shutil.copy(os.path.join(ROOT, cp.PIN), d)
    assert cp.check(d) == [], cp.check(d)  # the copy passes before .mcp.json is written
    text = servers if isinstance(servers, str) else json.dumps(servers)
    open(os.path.join(d, ".mcp.json"), "w").write(text)
    errs = cp.check(d)
    if expect is None:
        assert errs == [], errs
        print("ok    .mcp.json: a valid variant passes")
        return
    assert any(expect in e for e in errs), (expect, errs)
    print(f"ok    .mcp.json: {expect}")


with open(os.path.join(ROOT, ".mcp.json")) as fh:
    MCP = json.load(fh)
assert "swarm-mcp" in MCP["mcpServers"], MCP
SRV = MCP["mcpServers"]["swarm-mcp"]
mcp("{", ".mcp.json: Expecting property name")
mcp({"swarm-mcp": SRV}, "must be {")
mcp({"mcpServers": {"Swarm_MCP": SRV}}, "name must be kebab-case")
mcp({"mcpServers": {"r": {"type": "http", "url": "https://x"}}}, "local stdio servers only")
mcp(
    {"mcpServers": {"s": {**SRV, "args": ["-I", "${CLAUDE_PLUGIN_ROOT}/tools/nope.py"]}}},
    "${CLAUDE_PLUGIN_ROOT}/tools/nope.py not found in the plugin",
)
mcp({"mcpServers": {"s": {**SRV, "env": {"GH_TOKEN": "ghp_x"}}}}, "never a literal")
mcp({"mcpServers": {"s": {**SRV, "env": {"GH_TOKEN": "${GH_TOKEN:-ghp_x}"}}}}, "nor a :-default")
mcp(
    {"mcpServers": {"s": {**SRV, "args": ["${CLAUDE_PLUGIN_ROOT}/../outside.py"]}}},
    "${CLAUDE_PLUGIN_ROOT}/../outside.py is outside the plugin",
)
mcp({"mcpServers": {"s": {**SRV, "env": {"GH_TOKEN": "${GH_TOKEN}"}}}}, None)
mcp({"mcpServers": {"s": {"args": []}}}, "`command` must be a non-empty string")
assert SRV["args"] == ["${CLAUDE_PLUGIN_ROOT}/" + cp.LAUNCHER], SRV
print("ok    .mcp.json starts swarm-mcp through the launcher")


def pin(edit, expect, drop=None):
    """A copy with swarm-mcp.lock and the launcher, `edit`(lock text) written
    (or the file `drop` removed), fails with `expect`."""
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills", "tools"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    shutil.copy(os.path.join(ROOT, cp.PIN), d)
    assert cp.check(d) == [], cp.check(d)
    p = os.path.join(d, cp.PIN)
    with open(p) as fh:
        text = edit(fh.read())
    with open(p, "w") as fh:
        fh.write(text)
    if drop:
        os.remove(os.path.join(d, drop))
    errs = cp.check(d)
    assert any(expect in e for e in errs), (expect, errs)
    print(f"ok    pin: {expect}")


with open(os.path.join(ROOT, cp.PIN)) as fh:
    LOCK = fh.read()
COMMIT = cp.PIN_LINES["commit"].search(LOCK).group(0)
pin(lambda t: t.replace(COMMIT, 'commit = "main"'), 'must be commit = "<40 hex>"')
pin(lambda t: t.replace(COMMIT, COMMIT[:-3] + '"'), 'must be commit = "<40 hex>"')
pin(lambda t: t.replace(COMMIT, "# no commit"), "one `commit = ...` line (found 0)")
pin(lambda t: t + COMMIT + "\n", "one `commit = ...` line (found 2)")
pin(lambda t: t + 'commit = "main"\n', "one `commit = ...` line (found 2)")
pin(lambda t: t + 'repository = "someone/x"\n', "one `repository = ...` line (found 2)")
pin(
    lambda t: t.replace("swarm-routing/swarm-mcp", "someone/swarm-mcp"),
    'must be repository = "swarm-routing/swarm-mcp"',
)


def notag(t):
    return re.sub(r"^tag = .*\n", "", t, flags=re.M)


pin(lambda t: notag(t) + 'tag = "main"\n', 'must be tag = "vX.Y.Z"')
pin(lambda t: notag(t) + 'tag = "v1.2"\n', 'must be tag = "vX.Y.Z"')
pin(
    lambda t: notag(t) + 'tag = "v1.2.3"\ntag = "v1.2.4"\n',
    "at most one `tag = ...` line (found 2)",
)
pin(lambda t: t, "but swarm-mcp.lock is missing", drop=cp.PIN)
pin(lambda t: t, "but tools/mcp/swarm-mcp is missing", drop=cp.LAUNCHER)


def launcher_reads(old, new, expect):
    d = tempfile.mkdtemp()
    for sub in (".claude-plugin", "skills", "tools"):
        shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    shutil.copy(os.path.join(ROOT, cp.PIN), d)
    p = os.path.join(d, cp.LAUNCHER)
    text = open(p).read()
    assert old in text, old
    open(p, "w").write(text.replace(old, new))
    errs = cp.check(d)
    assert any(expect in e for e in errs), (expect, errs)
    print(f"ok    launcher: {expect}")


launcher_reads("swarm-mcp.lock", "other.lock", "does not read swarm-mcp.lock")
launcher_reads(
    "# <<< cached-checkout\n", "# <<< cached-checkout\ngit fetch x\n", "fetches or caches outside"
)
launcher_reads("cached_checkout_locked() {", "cached_checkout_lockd() {", "block differs from")
print("check-plugins self-test: OK")
