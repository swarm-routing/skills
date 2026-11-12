---
name: token-audit
description: "Measure and cut what an AI session costs in tokens: what it loads before its first tool call (CLAUDE.md, the AGENTS.md it imports, skill listings), which sections are large, stale or repeated in every repository, and, for a finished session, where its tokens actually went (the context of the first request, the tools called most, the largest results). Use it whenever agent files are written, reviewed or refactored (AGENTS.md, CLAUDE.md, CONTEXT.md, a skill), when someone says a session was expensive, slow to start or ran out of context, before attaching many repositories to one session, when deciding what belongs in an always-loaded file and what in a document read on demand, and when work a model repeats by hand should become a script. Use it even if the user only says the agent files feel long or asks why a chat used so many tokens. Script first: token_audit.py prints sizes and counts, so no transcript or file content enters the context."
license: MIT OR GPL-2.0-only
compatibility: Needs python3. Reads local files only and sends nothing anywhere. With skills.sh (npx skills add) the wrapper clones swarm-routing/skills once to find tools/token-audit/token_audit.py, which needs git and network access to github.com; SKILLS_TOOLS_DIR=<checkout> avoids it.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# token-audit

Everything a session loads at its start is sent again with every request it
makes. A file that costs 7,000 tokens once costs 700,000 over a hundred
requests, in every session, for everyone. So the cheapest token is the one
that is not in an always-loaded file, and the second cheapest is the one a
script reads instead of the model. This skill finds both.

```bash
SKILL="$CLAUDE_PLUGIN_ROOT/skills/token-audit"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
"$SKILL"/scripts/token-audit files .                      # what a session in this repository loads
"$SKILL"/scripts/token-audit files ../ARA ../Termite .    # several repositories attached to one session
"$SKILL"/scripts/token-audit files . --budget AGENTS.md=12000 --budget-loaded 16000   # as a gate: exit 1 when over
"$SKILL"/scripts/token-audit transcript <session>.jsonl   # where a finished session's tokens went
```

Inside a `swarm-routing/skills` checkout, `python3 -I
tools/token-audit/token_audit.py` is the same. Both commands take `--json`.

Two kinds of number come out, and a report must keep them apart:

- **`files` gives estimates.** Bytes are exact; tokens are bytes divided by
  3.5. A token count is specific to a model, and only that model's token
  counter gives the exact figure. The estimate is good for comparing files
  and for budgets, not for a bill. Do not send files to any service to count
  them: this skill works offline on purpose.
- **`transcript` gives measurements.** They are the usage the API reported
  for each request of the session.

## 1. Measure what a session loads

Run `files` on the repository, or on every repository the session will have
attached. Read, in this order:

1. **The total loaded at session start.** This is the fixed cost of every
   request. With several repositories it adds up: each one's files are loaded
   whether the task needs that repository or not.
2. **The largest sections.** A section is a `## ` heading and what follows it.
3. **The notes on each section.** `managed <block>` is text between
   `org-sync:begin/end` markers: the same in every repository, owned by a
   template. Dates and issue numbers mark status, the text that goes stale.
4. **Read on demand.** Markdown files the loaded ones link to. They cost
   nothing until a session opens them, which is where long material belongs.
5. **Sections identical in more than one repository** (with several
   repositories). That text is paid for once per repository attached.

## 2. Decide what each section is

For every large section, ask what a session loses if the text is not in front
of it from the first request. That gives four kinds:

| Kind | Test | Where it goes |
|---|---|---|
| Always needed | it changes how the agent behaves on any task here: an invariant, a rule that is easy to break, where the build and the checks are | stays, as short as it can be said |
| Needed for some tasks | a tool catalogue, a long how-to, a table of where things are, background and history | a document under `docs/`, with one line left behind that says **when** to read it |
| Status | dated sentences, "merged in #N", what is planned or in progress | out of the agent files: an issue, an epic, or a generated page. Status in prose is wrong within days, and a wrong line costs more than a missing one |
| Org-managed | between `org-sync` markers | not edited here. Change the template in `swarm-routing/.github` `templates/`; a per-repository edit is undone by the next sync and fails its check |

The line left behind is what makes the split work. "See docs/tools.md" tells
a session nothing; "Before changing a workflow or a release script, read
docs/tools.md (every tool, its commands and its self-test)" tells it when the
cost is worth paying. A pointer with no condition is either always followed,
which saves nothing, or never, which loses the content.

Nothing is deleted on size alone. A rule that moves keeps its words and gets
a pointer; a rule that goes is named in the summary with the reason.

## 3. Read where a session's tokens went

For a session that felt expensive, slow or that ran out of room, run
`transcript` on its JSONL file (Claude Code keeps one per session under
`~/.claude/projects/<project>/`; a subagent's transcript is its own file, and
several files can be given at once). Never open the transcript itself: it is
the whole session, and reading it costs what the session cost. The script
prints sizes, counts and a 60-character summary of each call's input.

- **Context of the first request**: the cost of starting, before any work. If
  it is large, section 1 says why.
- **Largest context, and requests**: a session's input cost is roughly its
  context times its requests, so a long session with a large context is the
  expensive shape. Splitting the work, or handing a narrow task to a subagent
  that reports a summary, changes it.
- **Per tool: calls and bytes of results.** A tool called dozens of times
  with small variations is a loop the model is running by hand. The script
  lists these as candidates for a script or a data file.
- **Largest results**: whole files read where a range or a search would do,
  or a command printing more than was needed.
- **Calls repeated with identical input**: something read twice.

## 4. Turn findings into changes

- **Agent files**: one PR per repository for its own sections. Run `files`
  before and after and put both totals in the PR.
- **Org-managed text**: one PR to the template, with the before and after of
  one repository and the number of repositories it applies to.
- **A loop the model ran by hand**: an issue for a script, with the tool, the
  number of calls and the bytes from the transcript audit as its evidence. A
  script that prints a summary replaces the calls for every later session
  (AntHocNet ADR-0014: raw data stays out of the context; the model reads a
  verdict).
- **A budget**: once a file is the size it should be, `--budget` keeps it
  there. Propose the number from the measurement; whether it becomes a gate
  is the maintainer's decision.

## 5. Report

Give the result in this shape, so two audits can be compared:

```
Loaded at session start: <bytes> bytes, about <tokens> tokens (estimate) -> <bytes> after
Largest sections: <section, bytes, kind> ...
Moved on demand: <what> -> <file>, read when <condition>
Status removed: <what>, now at <issue or page>
Not touched: <org-managed blocks>, to change through <template>
Session (measured): first request <tokens>, largest context <tokens>, <n> requests
Candidates for a script: <tool>, <calls> calls, <bytes> bytes
```

Leave out the lines that do not apply. Say "estimate" next to every token
figure that came from `files` and "measured" next to those from `transcript`.

## What not to do

- Do not shorten a rule until it stops being one. "Wire formats are
  versioned" is shorter than the rule and does not say what to do.
- Do not move an invariant out of the always-loaded file to meet a budget:
  raise the question instead. The budget serves the rules, not the reverse.
- Do not treat a smaller file as proof of a better one. If the repository has
  an onboarding eval (questions a fresh session must answer from the agent
  files), run it before and after; if it has none, say that the cut was not
  checked that way.
