---
name: rcapa
description: "Open an RCAPA ticket the moment a bug is found, then record the investigation on it step by step, and derive the RCAPA document from the ticket: an ns-3 bug (NS3-NNN, in swarm-routing/sim-tools) or a regression in a published library version (<PREFIX>-NNN, in that library's repository). Use whenever a task turns up a bug, a wrong number, a simulator misbehaviour or a regression in a released library, before investigating it further, and whenever an investigation step (hypothesis, source reading, reproduction, fix, duplicate search) has a result worth keeping. Script first: rcapa.py open creates the ticket with the form's title, labels and sections; log posts one fixed-shape comment per step; steps prints them; doc drafts the document's Timeline and Evidence to stdout."
license: MIT OR GPL-2.0-only
compatibility: Needs python3 3.11+, the gh CLI logged in (or GH_TOKEN) and network access to github.com (scripts/rcapa clones swarm-routing/.github tools/rcapa). open and log write issues; with a gh that cannot, --dry-run prints the payload to post with another GitHub tool.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# rcapa

A bug found and investigated but never ticketed is lost: the evidence lives
in one session. The rule is **ticket first, then investigate**, and the
ticket's comments are the investigation's record. CONTRIBUTING "RCAPA" and
"ns-3 bugs (RCAPA)" are the reference; this is the order.

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/rcapa"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
R="$SKILL/scripts/rcapa"                      # R open|log|steps|doc ...
```

`ORG_TOOLS_DIR=<checkout of swarm-routing/.github>` points the wrapper at a
local one. `"$R" <command> --help` is the CLI; never guess a flag.

## 1. Stop and open the ticket

The moment you find a bug during any task, stop what you were doing and
open the ticket, before reading more source or trying a fix. One line of
symptom is enough; the investigation fills the rest.

| What you found | Command |
|---|---|
| a bug in ns-3 itself | `"$R" open --repo sim-tools auto "<short description>" --kind ns3` |
| a regression in a published library version | `"$R" open --repo <library repo> auto "<short description>" --kind regression` |

- `auto` takes the next free ID (NS3-NNN, or the library's `<PREFIX>-NNN`
  from CONTRIBUTING's table). The command refuses an ID a ticket already
  has: look for the existing ticket first (step 2's duplicate search can
  run before, never instead of, the open).
- Add what you already know with `--field <id>=<text>`: for `--kind ns3`
  the ids are `versions`, `modules`, `context`, `symptom`, `reproducer`,
  `evidence`, `workaround`, `scope`, `acceptance`, `depends`, `refs`; for
  `--kind regression`, `releases` and `ns3` replace `versions` and
  `modules`. Add `--priority P1|P2|P3` and `--model model:…` as the issue
  taxonomy asks.
- `--dry-run` prints the request instead of sending it; use it to check the
  title and fields, then run without it.
- Name the ticket in your report and in every workaround, commit and PR
  that follows (`NS3-NNN`).

## 2. Log every step on the ticket

After each step of the investigation, post it before the next step:

```bash
"$R" log --repo <repo> <ID> --step <step> --text "<what>" \
    [--versions "<ns-3 / library versions>"] [--command "<what you ran>"] [--result "<what it printed>"]
```

`<step>` is one of:

| Step | When |
|---|---|
| `hypothesis` | you suspect a cause: say what and why |
| `source` | you read the code that decides it: file, line, what it does |
| `reproduce` | you ran the reproducer: `--command` and `--result` verbatim |
| `fix` | a fix or workaround: what changed and the check that now passes |
| `duplicate-search` | you searched for the same bug (ns-3 GitLab, our tickets): where, and the hits |
| `note` | anything else that belongs in the record |

A failed reproduction and a refuted hypothesis are steps too. `--command`
and `--result` carry the exact text, never a paraphrase or a number from
memory. `steps` prints the comments as JSON:

```bash
"$R" steps --repo <repo> <ID>
```

## 3. Derive the document

When the investigation is done, draft the RCAPA document from the ticket,
not from memory:

```bash
"$R" doc --repo <repo> <ID>      # stdout: Timeline and Evidence; --repo is required for a non-NS3 ID
```

It never writes a file. Put its output into the document (sim-tools
`docs/ns3-bugs.md` register row and doc for an NS3-NNN, the library's
`docs/rcapa/` for a regression), then link the ID from every workaround.
Upstream ns-3 reports go out only through swarm-routing/ns3-upstream-report;
this skill never posts to ns-3's GitLab.

## Rules

- Never investigate first and record afterwards; a ticket opened after the
  fix has no timeline.
- A ticket stays open until a release carries the fix (CONTRIBUTING
  "RCAPA"); do not close one from here.
- `open` and `log` post to GitHub as the caller. They take no secret and
  send nothing but the ticket's own text: keep paths, tokens and private
  repository names out of `--text`, `--command` and `--result`.
