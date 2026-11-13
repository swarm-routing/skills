---
name: bestpractices
description: "OpenSSF Best Practices badge (bestpractices.dev) for a repository: register it, propose its passing-level answers from the repository's evidence, keep them current, and answer one criterion pasted from the form. Use whenever someone mentions the OpenSSF / CII Best Practices badge, bestpractices.dev, a project id there, .bestpractices.json, `bestpractices_project`, the weekly `[bestpractices]` drift issue, or pastes a criterion (\"The project MUST ...\", a `<criterion>_justification` field) and wants a justification. Script first: bestpractices.py derives the answers, the registration and proposal links and the drift report; nothing logs in or submits, the maintainer reviews and saves on the site."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 3.11+, gh (authenticated, for tracker counts) and network access to github.com (scripts/bestpractices clones swarm-routing/.github tools/bestpractices; scripts/responses runs this repository's tools/tracker-responses) and to www.bestpractices.dev (public read-only JSON).
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# bestpractices

The OpenSSF Best Practices badge is a self-certification: a person answers
each criterion on bestpractices.dev with a status (Met, Unmet, N/A, ?) and a
justification. Answers written from memory claim things a repository does
not show, and the site publishes them. This skill derives every answer from
evidence on `main`, hands the maintainer something to review, and keeps the
site and the repository in step.

**What can never be automated, and why.** bestpractices.dev has no token
write API. The maintainer decided (2026-11-13) that nothing logs in to the
site or stores a password for it: no agent, no workflow. So every change on
the site is made by the maintainer, logged in, who reviews a proposal and
clicks **Save**. You prepare; you never submit, never ask for credentials,
never drive a browser session on the site. The only site requests you make
are the public read-only ones the script makes (`/projects.json?url=…`,
`/projects/<id>.json`).

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/bestpractices"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
BP="$SKILL/scripts/bestpractices"
"$BP" answers REPO_DIR [--slug OWNER/NAME] [--write]       # derive the answers; --write: .bestpractices.json
"$BP" register OWNER/NAME --dir REPO_DIR [--answers FILE]  # registered? id + proposal links, else where to register
"$BP" check --repos NAME[=ID][,...]                          # drift, read-only (never --issues by hand)
"$SKILL/scripts/responses" OWNER/NAME --label bug|enhancement  # tracker counts for the response criteria
```

Inside a `swarm-routing/.github` checkout, `python3 -I
tools/bestpractices/bestpractices.py …` is the same; `ORG_TOOLS_DIR=<checkout>`
points the wrapper at a local one.

## Facts to carry into every answer

- **Owner-only criteria.** Never answer these, never put them in a proposal
  link or `.bestpractices.json` as anything but `?`, never suggest submitting
  them without the maintainer: `know_secure_design`, `know_common_errors`
  (self-assessments), `vulnerabilities_fixed_60_days`,
  `vulnerabilities_critical_fixed`, `no_leaked_credentials`,
  `static_analysis_fixed` (facts behind the Security tab and private
  reports). List them for the maintainer to answer on the site.
- **Response history is counted, not guessed.** `report_responses`,
  `enhancement_responses` and `vulnerability_report_response` depend on the
  tracker's history. bestpractices.py leaves them `?`; if asked, count them
  with `responses` (section 4) and give the maintainer the numbers and a
  draft justification to submit themselves.
- **Licence of the answers.** bestpractices.dev releases submitted data under
  CDLA-Permissive-2.0 (https://cdla.dev/permissive-2-0/). Write nothing in a
  justification that cannot be published under it (no private repository
  names or paths, no unpublished results, no personal data).
- **Justifications cite evidence by full https URL**, on `main`
  (`https://github.com/<owner>/<repo>/blob/main/<path>`, a `#anchor` where
  one exists), so the weekly check can tell when a path disappears.
- **The badge** is rendered by org-sync from the repository's
  `.github/org-sync.toml` top-level key `bestpractices_project = "<id>"`
  (badge kind `bestpractices`, after `scorecard`; a repository with its own
  `badges` list adds `"bestpractices"` there).
- **Worked example:** AntHocNet is project 16656
  (https://www.bestpractices.dev/projects/16656).

## 1. Register a repository

```bash
git clone -q https://github.com/swarm-routing/NAME REPO_DIR   # a clean checkout of main
"$BP" register swarm-routing/NAME --dir REPO_DIR
```

The answers are read from the working tree but cite `blob/main` URLs, so the
checkout must be exactly `main`: a fresh clone, or `git fetch origin && git
checkout origin/main` with `git status --porcelain` empty. With local edits,
stop and use a fresh clone instead.

- **Not registered:** it says where to register:
  https://www.bestpractices.dev/en/projects/new with the repository's URL
  (the site has no pre-filled registration form). The maintainer adds it
  there, logged in; then run `register` again for the id and the proposal
  links.
- **Registered:** it prints the project id, the line
  `bestpractices_project = "<id>"` and the proposal links (next section).
  If `.github/org-sync.toml` lacks the line, open a PR adding it (top-level
  key, before any `[table]`), then `org_sync.py apply .` renders the badge in
  the same PR (`org-repo` skill).

## 2. Propose the answers

```bash
"$BP" answers REPO_DIR > /tmp/bp.json        # stderr: "bestpractices: ? N, Met N, N/A N"
```

Review the derived file before it goes anywhere: each `Met` names evidence
that really says what the justification claims (open the URL's file on
`main`), and each `?` is either owner-only, one the tool leaves to the
maintainer on purpose (`test_most`, `tests_are_added`: coverage measured is
not coverage of most code, a written test policy is not proof it was
followed), or truly without evidence. Where
the repository does show evidence the script missed, fix the evidence or say
so; do not hand-promote a `?` to `Met` without a URL.

Two ways to the site, both ending with the maintainer's Save:

- **The file.** `"$BP" answers REPO_DIR --write` writes `.bestpractices.json`
  at the top level; commit it in a PR. After it merges, the maintainer
  re-saves on the site with **"Save (and continue) 🤖"** (the robot button),
  which proposes the file's answers. Do this again whenever the file changes.
- **Proposal links.** `"$BP" register swarm-routing/NAME --dir REPO_DIR
  [--answers reviewed.json]` prints
  `https://www.bestpractices.dev/en/projects/<id>/passing/edit?<criterion>_status=…&<criterion>_justification=…`,
  split into links under ~6000 characters with a criterion's status and
  justification never split, owner-only criteria left out. Hand the links
  over as a numbered list: "open each logged in, review the proposed
  answers, click Save". Opening a link saves nothing.

Report the counts (Met / N/A / ?), the owner-only list, and anything you
could not evidence.

## 3. Keep it current

The weekly `bestpractices.yml` workflow in `swarm-routing/.github` runs
`check --issues` with the bot's token and keeps one `[bestpractices] N
finding(s)` issue per repository. By hand, run it read-only:

```bash
"$BP" check --repos NAME            # NAME=ID if the config has no key yet; exit 0 clean, 1 drift, 2 unreadable
```

Findings and their fix:

| Finding | Fix |
|---|---|
| registered, but no `bestpractices_project` key | PR adding the key (section 1) |
| site answer differs from `.bestpractices.json` | decide which is right from `main`; fix the file by PR, or give the maintainer the criterion to re-save |
| justification URL's path gone from `main` | regenerate (`answers --write`), PR, then the maintainer re-saves with the robot button |
| level lost (`lost_<level>_at` after `achieved_<level>_at`) | find the criterion that turned Unmet or `?` and report it to the maintainer |

Never run `check --issues` yourself (that is the workflow's job, with its
token); never edit the site to clear a finding.

## 4. Answer one criterion pasted from the form

The maintainer pastes a criterion's text (or its id). Return **one**
paste-ready status and justification.

1. Map the text to its criterion id (the form's order is `PASSING` in
   bestpractices.py). If it is owner-only, say so and stop: give the facts
   you can check (links to the Security tab, the advisories page) but no
   status.
2. Find the evidence on `main`: `git fetch -q origin`, then search
   `origin/main` (`git grep -n PATTERN origin/main -- .`, `git show
   origin/main:PATH`), never a local branch that may be stale. Prefer what
   CI enforces (a workflow, a required check) over what a doc promises.
3. Tracker numbers come from `responses` (this repository's
   `tools/tracker-responses/responses.py`), never from a guess or from
   `gh api --paginate` (the proxy rejects its next links; the script asks for
   each `page=` itself):

   ```bash
   "$SKILL/scripts/responses" swarm-routing/NAME --label bug           # report_responses
   "$SKILL/scripts/responses" swarm-routing/NAME --label enhancement   # enhancement_responses
   ```

   It counts the issues (not PRs) created 2-12 months ago and classifies each
   by GitHub's `author_association`: acknowledged (filed by the project, a
   project comment, or closed by the project), unanswered (only the reporter
   acted) or unverified (closed by someone whose role it cannot see), and
   prints the reporters and the issue-search URL. Exit 2 means a request
   failed and nothing was counted: say so, do not report a number. Quote the
   breakdown as printed (if every report was filed by the project, the
   justification says so), and look at each unverified issue before counting
   it. `vulnerability_report_response` depends on private reports: the
   maintainer reads the repository's security advisories.
4. Write the justification: one or two sentences, every claim backed by a
   full https URL, nothing that cannot be published under
   CDLA-Permissive-2.0. Output exactly:

   ```text
   <criterion>: Met | Unmet | N/A
   <justification>
   ```

   For a response-history criterion, label it a draft for the maintainer to
   submit. If the evidence is missing, answer Unmet (or "no evidence on
   main") and name what would make it Met; never Met without a URL.
