---
name: sonar-triage
description: "Record a reviewed SonarQube Cloud finding as a false positive (or an accepted wontfix) where the quality gate reads it, through swarm-routing/.github's decisions.toml and the sonar-triage workflow: review the finding, read its key, rule, file and line from SonarQube Cloud's API, add the entry with a reason, validate and plan, open the PR, then plan and apply after merge. Use whenever a SonarQube Cloud quality gate is red on a finding someone calls a false positive, a Sonar security hotspot or vulnerability needs a verdict, someone asks to mark, accept, dismiss or exclude a Sonar finding, or `sonar_triage.py plan` refuses an entry (the finding moved). Script first: sonar_triage.py checks every entry against the live finding; you never mark a finding in the SonarQube Cloud UI, add a rule or path exclusion, or change a quality gate."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 3.11+ and network access to github.com (scripts/sonar-triage clones swarm-routing/.github tools/sonar-triage) and sonarcloud.io (public read API, no token). gh to open the PR and dispatch the workflow.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# sonar-triage

SonarQube Cloud's gate fails on findings its scanner cannot judge: a CLI
argument it calls tainted, a pattern from the repository's own schema it
calls a ReDoS. The org records each reviewed verdict as data, one entry per
finding key in `swarm-routing/.github` `tools/sonar-triage/decisions.toml`,
and a dispatched workflow marks it with the org token, a comment and a link
to the review (swarm-routing/.github#425, #448). Rules, path exclusions,
quality gates and profiles stay as they are (maintainer decision
2026-11-15); a session never marks a finding itself.

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/sonar-triage"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
ST="$SKILL/scripts/sonar-triage"
"$ST" findings --repos <name>     # read-only, no token: the open findings, and which the file records
"$ST" plan --repos <name>         # read-only, no token: every entry of that repository against the live finding
```

To edit the file, work in a checkout of `swarm-routing/.github` on a
`claude/` branch and set `ORG_TOOLS_DIR=<that checkout>`, so the wrapper
reads your `decisions.toml`, not `main`'s.

## 1. Review the finding first

A verdict is a review, not a way to turn the gate green. Read the flagged
code at the file and line, and the rule's description
(`https://sonarcloud.io/coding_rules?open=<rule>`). Then decide:

| The finding is | Do |
|---|---|
| real | fix the code in the repository, with a test; no entry |
| wrong (the value is a CLI argument, a committed file, already validated, ...) | `falsepositive`, with a reason |
| true as stated, accepted for a stated reason (a build image that runs as root) | `wontfix` (the script uses `accept` where SonarQube Cloud offers that) |
| unclear | ask the maintainer, with the code and the rule; no entry |

The review goes in an issue (the repository's, or the open triage issue the
file's comments link): what the code does, why the rule does not apply.

## 2. Print the entry from the API

Never type a key, rule, file or line. `findings` lists the open findings of
the project (`swarm-routing_<repo>`) on `main`, a row each, with `-` where the
file records nothing; `entry` prints the block for the key you reviewed:

```bash
"$ST" findings --repos <repo>
ORG_TOOLS_DIR=<checkout> "$ST" entry <KEY> --reason <id> [--decision wontfix]
```

`entry` refuses a key already in the file, a reason id not in `[reasons]`
and an unknown key. A hotspot takes `--decision SAFE|ACKNOWLEDGED|FIXED`.

## 3. Add the entry, validate, plan

Paste the printed block under the repository's group in `decisions.toml`.
`reason` is an id from the file's `[reasons]` table. Reuse one whose text is
true of this finding word for word; otherwise add a new id whose text says
why, in the review's words, before running `entry`. Then:

```bash
ORG_TOOLS_DIR=<checkout> "$ST" validate
ORG_TOOLS_DIR=<checkout> "$ST" plan --repos <repo>      # your entry `open`, nothing refused
python3 -I tools/sonar-triage/sonar_triage.py --self-test   # in the checkout, if you touched the script
```

`plan` refuses the whole run when an entry's key is gone, or its project,
rule, file or line differ from the live finding, or it was resolved another
way. For a refused entry of your own, print it again (step 2). For an
existing entry whose finding moved (the code changed), the old review no
longer holds: review it again; replace the entry only if the verdict still
stands, or drop it.

Open the PR in `swarm-routing/.github`, `chore(sonar-triage): record <n>
reviewed finding(s) in <repo>`, the body linking the review and pasting the
`plan` table rows.

## 4. After merge: plan, then apply on request

The `sonar-triage` workflow (`workflow_dispatch`: `mode` plan or apply,
optional `repos`) runs with the org `SONAR_TOKEN`:

```bash
gh workflow run sonar-triage.yml -R swarm-routing/.github -f mode=plan -f repos=<repo>
```

Read the run's summary (it should match your local plan, now with the
transition the token may make). Dispatch `mode=apply` only when the user
asks for it. Then re-read the gate:
`https://sonarcloud.io/api/qualitygates/project_status?projectKey=swarm-routing_<repo>&branch=main`.
A re-run is a no-op (`done`).

## Rules

- No marking in the SonarQube Cloud UI, no `sonar.issue.ignore`, no
  exclusion in `sonar-project.properties`, no quality-gate change: the file
  is the record, and every entry passed review in a PR.
- Never apply from a session with a personal token; the workflow does it.
- A finding you could not review stays open; say so.

## Report

```
<repo>: <n> finding(s) reviewed: <k> falsepositive, <w> wontfix, <f> fixed in code, <u> left open (why)
entries: .github PR #N (plan: <n> open, 0 refused) · after merge: plan run <url>, apply <done|not asked>
gate: <OK | ERROR: what still fails it>
```
