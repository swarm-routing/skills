# 0002. swarm-mcp is a local, read-only MCP server over the org's scripts

- **Status:** accepted (the maintainer asked on 2026-11-22 for this design
  note and the prototype together; that request is the acceptance of #185's
  first criterion)
- **Date:** 2026-11-22
- **Issue:** #185 (part of swarm-routing/.github#672, decisions 20 and 23)

## Context

The org's procedures are skills over scripts (golden rule 11): the script
does the work, the agent reads its summary. An agent reaches those scripts
today through a skill's wrapper and the Bash tool, which costs a skill load,
a shell command it has to compose, and the script's whole output in context.
The Model Context Protocol (MCP) lets a client call a named tool with typed
arguments and get its result back, without the shell and without the skill
text, in any MCP client (Claude Code, Codex, Cursor, Copilot, …).

The maintainer decided on 2026-11-22 (swarm-routing/.github#672) that a
`swarm-mcp` prototype lives in this repository, as an extension of the
`protocol-review`, `fidelity-sheet` and `release` skills rather than as new
skills (decision 20), and that it is scheduled now (decision 23). Two
questions were open: the language (swarm-routing/.github ADR-0002 makes
pipelines Go and lets skill scripts stay Python), and the packaging.

This repository is a trust boundary (golden rule 10): what merges here runs
in every session of every repository that enables the plugin. An MCP server
bundled with the plugin starts in all of them.

## Decision

### What it is

`swarm-mcp` is a **local stdio MCP server**, `tools/swarm-mcp/swarm_mcp.py`,
run by the agent session; it needs no hosted service, no account and no
port. Each tool runs **one read-only command** of an org script and returns
its exit status and its summary text:

| Tool | Runs | Wrapper |
|------|------|---------|
| `fidelity_check` | `fidelity.py check FILE` | `skills/fidelity-sheet/scripts/fidelity` |
| `fidelity_row` | `fidelity.py row FILE [--protocol NAME]` | same |
| `fidelity_verify` | `fidelity.py verify FILE --text KEY=PATH ...` | same |
| `protocol_review` | `check_invariants.py [REPO] --base REF [--pr-body FILE]` | `skills/protocol-review/scripts/check-invariants` |
| `release_ready` | `release_check.py ready REPO_DIR [--repo O/N] [--version X.Y.Z]` | `skills/release/scripts/org-tool release-check` |
| `release_after` | `release_check.py after O/N --tag vX.Y.Z [--repos A,B]` | same |
| `lock_verify` | `release_lock.py verify LOCK` | `skills/dependency-bump/scripts/org-tool release-lock` |

The rules every tool keeps, which a review of a new tool checks:

1. **Read-only commands only.** No tool maps to a command that writes a file,
   a branch, an issue or a release (`fidelity.py skeleton`/`bib sources`,
   `release_lock.py bump --write`, `zenodo.py` writes and every dispatch stay
   out). A new tool names its command in this table.
2. **The script's summary, never raw data, and a cap.** The result is
   `<tool>: exit N (ok|findings|error)`, the script's stdout, then its stderr,
   trimmed to `SWARM_MCP_MAX_CHARS` (default 6000 characters for stdout, a
   quarter of that for stderr), keeping the head and the tail (where the
   verdict line is) with a marker naming the cut. Exit 1 is a verdict with
   findings (`isError: false`); any other non-zero exit, a timeout
   (`SWARM_MCP_TIMEOUT`, default 300 s, the process group killed) or a
   wrapper that cannot start is a tool error (`isError: true`).
3. **Arguments are data, never options.** Each tool has a closed input schema
   (`additionalProperties: false`), versions, tags, repositories and refs have
   patterns, and no string may start with `-`, so a caller cannot reach a
   flag the table does not list. The command is an argv list; no shell
   parses it. Relative paths resolve against `CLAUDE_PROJECT_DIR` (set by
   Claude Code), else the server's working directory.
4. **No network of its own, no token, no write.** The server opens no
   connection and reads no credential. A script reaches the network only as
   it does when a person runs it (`git ls-remote`, `gh` with the user's own
   login for `release_after`, public HTTPS reads). The environment passes
   through to the script unchanged and is never printed.

### Where the scripts come from

The server does not find the org scripts itself: it runs the skills'
wrappers, so there is one convention, the one every skill already uses.
`ORG_TOOLS_DIR=<checkout of swarm-routing/.github>` names a local checkout
(the sibling `../.github` when it is one); otherwise the wrapper's
`cached-checkout` block fetches `swarm-routing/.github` at `ORG_TOOLS_REF`
(default `main`) into an immutable snapshot under
`${XDG_CACHE_HOME:-~/.cache}/swarm-routing/checkouts/`. That fetch is the
only network step outside the scripts, and it is the same one the skills
make.

### Language: Python, stdlib only

The server is Python with the standard library alone: JSON-RPC 2.0 over
stdio is a few hundred lines, and a third-party MCP SDK would be the first
dependency a session installs from this repository. swarm-routing/.github
ADR-0002 makes **pipelines** (code a workflow runs) Go and lets **skill
scripts** stay Python; swarm-mcp is neither a pipeline nor run by a workflow,
it is the agent-side face of the skills' scripts and runs where they run,
from a plugin checkout, with the `python3` the wrappers already need. A Go
binary would need a build step or a published binary per platform in a
repository that ships no builds. If a pipeline ever needs these verdicts it
calls the scripts (or their Go ports) directly, not this server.

### Protocol

The server is **dual-era** (MCP specification, "Versioning and
Compatibility"): a modern request carries
`params._meta["io.modelcontextprotocol/protocolVersion"]` = `2026-07-28` and
is served statelessly, with `resultType: "complete"`; `server/discover`
returns the supported versions, the `tools` capability and `serverInfo` in
`_meta`. A legacy client opens with `initialize` and gets the version it
asked for among `2025-11-25`, `2025-06-18`, `2025-03-26` (else `2025-11-25`).
An unknown version is `UnsupportedProtocolVersionError` (-32022) listing the
supported ones; an unknown tool is -32602, an unknown method -32601, bad
JSON -32700, a batch -32600 (MCP has no batches); notifications get no
reply. Methods: `initialize`, `server/discover`, `ping`, `tools/list`,
`tools/call`. `tools/list` is in a fixed order, each tool annotated
`readOnlyHint: true`.

### Packaging and running it

- **Claude Code**: the plugin's `.mcp.json` at the plugin root (Claude
  Code's default location for a plugin's MCP servers):

  ```json
  {"mcpServers": {"swarm-mcp": {"command": "python3",
    "args": ["-I", "${CLAUDE_PLUGIN_ROOT}/tools/swarm-mcp/swarm_mcp.py"]}}}
  ```

  Every repository that enables the `swarm-routing` plugin gets it with the
  plugin; nothing is added to any repository's `.claude/settings.json`. Its
  tools appear under the server's name (the client prefixes each tool name
  with the plugin's and the server's). In a session opened in this repository, the same file
  is read as a project `.mcp.json`, where `${CLAUDE_PLUGIN_ROOT}` is unset:
  Claude Code asks before it starts a project server, and the answer there
  is no (develop against `python3 -I tools/swarm-mcp/swarm_mcp.py`).
- **Any other MCP client, or by hand**, from a checkout of this repository:

  ```bash
  python3 -I tools/swarm-mcp/swarm_mcp.py               # the server, on stdin/stdout
  python3 -I tools/swarm-mcp/swarm_mcp.py --list        # its tools, one line each
  python3 -I tools/swarm-mcp/swarm_mcp.py --self-test   # what make test runs
  ```

  registered in the client's own MCP configuration with that command, and
  `ORG_TOOLS_DIR` in its environment where a local `.github` checkout should
  be used. skills.sh installs skills only, not this server.
- **Validation**: `tools/checks/check-plugins.py` checks `.mcp.json`: an
  `mcpServers` map and nothing else, kebab-case names, local stdio servers
  only (`command`, `args`, `env`; never `url`, `http` or `sse`), every
  `${CLAUDE_PLUGIN_ROOT}/<path>` a file in the plugin, every `env` value a
  `${VAR}` reference (no literal, so no committed secret).

### Versioning

The server has no version of its own: `serverInfo.version` is the plugin's
(`.claude-plugin/plugin.json`), and a change to the server bumps it with the
marketplace entry, `.cz.toml` and `CITATION.cff` in the same PR (golden rule
12). A tool's name, its arguments and their meaning are a contract for the
agents and skills that call it: a tool is added, or an optional argument is
added, in a minor version; a rename, a removed tool or a changed meaning is a
new tool name, with the old one kept until a major version.

### Trust boundary (golden rule 10)

The server adds no capability a session does not already have through the
Bash tool and the wrappers: the same scripts, the same arguments a skill
documents, minus every write. This PR is its review; a later change that
adds a tool, an argument or a network step is reviewed as a change to every
session that enables the plugin, against the four rules above. The client
still shows each call and can deny it.

### Out of scope

- Any tool that writes, dispatches a workflow, comments, or bumps a lock.
- A hosted or remote MCP endpoint (swarm-routing/swarm-routing.github.io#238
  stays deferred), HTTP transports, authentication.
- Resources, prompts, sampling, elicitation, subscriptions and
  `listChanged`: the tool list is fixed for a plugin version.
- The other skills' scripts (docs-review, pr-status, lit-search, …):
  candidates for later tools, each a reviewed PR.
- Structured output (`structuredContent`): the summary text is the
  contract the scripts already keep (AntHocNet ADR-0014).

## Consequences

- An agent gets a verdict in one typed call, without composing a shell
  command or loading a skill, and with a bounded result size.
- The scripts stay the single implementation: the server only maps tool
  arguments to their argv, so a script's fix reaches the MCP tool at once.
- Every session that enables the plugin can start the server; its whole
  surface is the seven read-only commands above, and widening it is a
  reviewed change here.
- The org MCP standard in swarm-routing/.github refers to this server by its
  name, `swarm-mcp`, and the run command above.
- Ruled out: write tools in this server, a third-party MCP SDK, and finding
  the org scripts any other way than through the skills' wrappers.
