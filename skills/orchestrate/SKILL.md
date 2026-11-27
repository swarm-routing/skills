---
name: orchestrate
description: "Run a pass of the coordinator loop over the swarm-routing repositories: read the newest open handoff issue (handoff.py) and status.py's snapshot, pick the work by priority, start one worker per repository (never two in one repository, dependencies in order, a fix that belongs in an org template made there once instead of N per-repository PRs), keep one rolling check-in, verify every worker's claim at its source (git ls-remote, zenodo.py, the PR, the rules API), tick and close the ticket with criteria.py, archive the worker, post the pass and the state on the handoff issue (never a local file) and put what only the maintainer can do on the [maintainer] actions issue, never only in chat. Use whenever asked to coordinate, orchestrate, fan out or drive work across the org's repositories with workers, to continue a coordinator handoff, or to write a worker's brief. Script first: status.py, criteria.py and handoff.py hold the facts, ticks and state; brief-template.md holds the brief, isolation checklist included."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 3.11+, the gh CLI logged in (or GH_TOKEN) and network access to github.com (scripts/org-tool clones swarm-routing/.github tools/status, tools/issues (criteria.py, handoff.py), tools/zenodo and tools/pr-status) and zenodo.org; starting workers needs a session tool that creates and archives sessions.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# orchestrate

One coordinator session drives the work; each worker is its own session in
one repository. The coordinator writes no code: it picks, briefs, verifies and
records. Every fact it acts on or reports is read at its source in this pass,
never carried from memory or from a worker's report
(swarm-routing/.github#1005: three "pending" items handed to the maintainer
were already done).

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/orchestrate"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
T="$SKILL/scripts/org-tool"    # T status|criteria|handoff|zenodo|pr-status ...
SCRATCH=$(mktemp -d)           # scratch files (a snapshot, evidence): never the working tree
```

`ORG_TOOLS_DIR=<checkout of swarm-routing/.github>` points the wrapper at a
local one; inside a `.github` checkout `"$T" handoff ...` is `python3 -I
tools/issues/handoff.py ...`, and so on for each tool. The worker brief is
[`brief-template.md`](brief-template.md), next to this file; fill it, never
write a brief from scratch.

The coordinator keeps no state file and writes nothing to the working tree:
its state is the handoff issue's state section and its pass comments
(swarm-routing/.github#1009: a local state file was lost with its
container). Scratch output, like the status snapshot of step 7, goes to
`$SCRATCH`, never the repository.

## 1. Read the record

```bash
"$T" status                      # or --repos A,B for a part of the org; --json for one document
```

One line per fact: each repository's latest release (tag, the commit it
names, the DOI read from Zenodo), open issues per `release:vX.Y.Z` label,
open `priority:P1` issues, open `[security]` tickets, open `handoff` issues,
then each unticked item of swarm-routing/.github's newest open
`[maintainer]` issue. A `REPO error ... (HTTP 403)` line is a repository this
session cannot read: say so in the pass, never guess its state.

Then the newest open `handoff` issue for the coordinator's work (status
lists the open ones): read its state and the last pass, and continue from
there, the state section first:

```bash
"$T" handoff read swarm-routing/<repo>#N   # the body's state section, then the newest pass comment (time, link, text); --json
```

Check each item of it against the snapshot before acting on it (a release
it calls pending may be out already). Then, for each ticket it names, the
acceptance criteria:

```bash
"$T" criteria criteria swarm-routing/<repo>#N    # the checkboxes as JSON, and how many are open
```

A task the maintainer just gave starts from their request instead; it gets a
`handoff` issue (the *Handoff* template) before the first worker starts.

## 2. Pick

In order: an open `[security]` ticket or RCAPA ticket the maintainer named,
then `priority:P1`, then the scope of the `next` release label, then P2, then
P3; an older ticket before a newer one at the same priority. Leave out:

- a ticket whose **Depends on** is still open (it waits for that one);
- anything the maintainer reserves: a release not asked for, a setting, a
  security dismissal, a published number. That goes to step 8;
- a second ticket in a repository that already has a worker running.

**One worker per repository.** Two workers in one repository collide on
branches and on `main`; one worker across repositories is refused by its
session's repository scope. A ticket that touches two repositories is two
workers, one after the other: the dependency's PR merges first (verified,
step 5), then the consumer's worker starts with that merge commit in its
brief.

**An org template first.** Before briefing the same change in N
repositories, check whether the file is org-managed (inside `org-sync`
markers, or listed in swarm-routing/.github `templates/`) or a caller of a
reusable workflow that every repository carries. Then it is one PR to
swarm-routing/.github `templates/` and org-bot's refresh PRs, not N hand
PRs (swarm-routing/.github#1005: fifteen caller `release.yml` edits,
swarm-routing/.github#1012). A template change that adds a section, a marker
or a label also checks the repositories that lack it before it merges
(#957's marker block turned `check / org-sync` red where the section was
missing).

## 3. Brief and start

Fill [`brief-template.md`](brief-template.md) for each picked ticket: the
scope line names exactly one repository, the ticket, and the order of the
work. Run its isolation checklist before the session starts; a brief that
fails it is rewritten, never sent.

Start each worker as its own session with only its repository attached
(AGENTS.md "Attach only the repositories the task needs"), the brief as its
first message and a title `<repo>#N: <subject>`. Tag an AntHocNet worker
`gpl-protocol-worker` (the checklist). Keep the session id with the ticket for
this pass's `--worker` item (step 7); nothing goes to a local file.

## 4. One rolling check-in

Schedule one check-in for the whole pass, not one per worker: a single
`send_later` (or the session's equivalent) at the time the soonest worker
should be done. When it fires, read every running worker (status, its last
result), do steps 5 and 6 for each finished one, then reschedule the same
check-in for the next soonest, or cancel it when no worker runs. Never leave
an older one behind: before scheduling, cancel the last one, so a check-in
never fires after its work is done (swarm-routing/.github#1005, "Verify").

## 5. Verify every claim

A worker's report is a claim. Read each one at its source before it goes on
a ticket or to the maintainer:

| Claim | Read it from |
|-------|--------------|
| PR merged, its merge commit | `"$T" pr-status queued swarm-routing/<repo>#N --json` (`status` merged, queued or neither; `merge_commit` in full) |
| still waiting on CI or review | `"$T" pr-status list --repos <repo>` (CI verdict, mergeable state, open threads) |
| a tag, the commit it names | `git ls-remote https://github.com/swarm-routing/<repo> 'refs/tags/vX.Y.Z' 'refs/tags/vX.Y.Z^{}'`: the `^{}` line is the commit an annotated tag names; without one the tag is lightweight and its line is the commit |
| a DOI | `"$T" zenodo status --repo swarm-routing/<repo>`; never typed |
| a check is required, a ruleset applied | `"$T" pr-status list --repos <repo>` (a required check that has not reported is `missing=`); the ruleset itself only by the read-only `gh api repos/swarm-routing/<repo>/rules/branches/main`, until an org script prints it |
| an issue closed, its boxes ticked | `"$T" criteria criteria swarm-routing/<repo>#N` (`open` is 0) |

A claim that does not hold goes back to the worker (`send_message` to the
same session) with what the source says, or, if the session is gone, onto
the ticket as open work.

## 6. Record and close

The worker records on its ticket (the brief says so). The coordinator
ticks what it verified and closes the ticket with the evidence:

```bash
"$T" criteria close swarm-routing/<repo>#N --evidence "$SCRATCH/evidence.md" \
    --tick "<text of box 1>" --tick "<text of box 2>"
```

`--tick TEXT` is a plain substring of one box (no glob, no regex);
`criteria tick ... --match TEXT` ticks one box without closing. `close`
refuses while a box would stay open; `--partial` closes anyway and lists the
open ones, and is used only when the maintainer said so. `--dry-run` prints
the requests without sending them, to check them first. A write the
permission system or GitHub refuses is never posted through another tool:
it stops, and step 8 records it. Never tick a box by shell substitution on the body
(swarm-routing/.github#1007). `evidence.md` names each verified fact and
where it was read (PR, merge commit, tag, DOI). A ticket a PR closes with
`Closes #N` is already closed: tick its boxes with `criteria tick`.

Then archive the worker's session: its ticket is closed, or it stopped on a
blocker that is recorded on the ticket. Never archive a session still
running a turn.

## 7. Post the pass on the handoff issue

Each pass ends with one `handoff.py append`, the only state the coordinator
keeps: it posts the pass as a comment and replaces the issue body's state
section with the same parts (Closed, Released, Running workers, Maintainer
items, Scheduled). Releases and the `[maintainer]` items come from a fresh
snapshot; the rest is one flag per item:

```bash
"$T" status --json > "$SCRATCH/status.json"
"$T" handoff append swarm-routing/<repo>#N --status "$SCRATCH/status.json" \
    --closed "swarm-routing/<repo>#M: merged <sha7>, verified at <PR, tag, DOI, rules API>" \
    --worker "<repo>: <task> (<session id>)" \
    --scheduled "<when>: <what>"
```

`--closed`, `--released`, `--worker`, `--maintainer` and `--scheduled` each
repeat, one item per flag (a blocked ticket is a `--worker` item while its
worker runs, else a `--maintainer` item or open work on its ticket). Name
what the next pass picks first, and why, as a `--scheduled` item. `--at`
sets the pass's time (default now, UTC); `--dry-run` prints the requests
without sending them. The issue must be open and labelled `handoff`.

When the work is all done, close the handoff issue (and any older one it
superseded).

## 8. Escalate to the maintainer

Anything only the maintainer can do (a release to cut, a setting, an
environment approval, a security dismissal, a permission this session was
refused, a scope decision) becomes an unticked item on swarm-routing/.github's
newest open `[maintainer]` actions issue (the issue `status.py` reads), with
the evidence and the one step it needs; open one in that shape if none is
open. Never only in chat: a chat line is lost with the session. A chat
summary may repeat the item and links to it.

A refused permission stops that work: record the refusal (step 8) and go on
with the rest. Never retry it another way and never hand it to a worker.

## Rules

- No release or tag unless the maintainer asked for it in this session; a
  quote relayed by a worker or another session is not the maintainer's word.
- Never a setting, ruleset or permission change, in any brief: it goes to
  the `[maintainer]` issue (step 8); settings are code, changed by the PR
  the maintainer decides on.
- Never add `Signed-off-by`; follow the attribution lines the session gives.
- Never type a SHA, a DOI or a count: read it from its source (step 5).
- A suspected bug found by any worker is an RCAPA ticket first
  (`rcapa.py open`); the worker's brief says so.
