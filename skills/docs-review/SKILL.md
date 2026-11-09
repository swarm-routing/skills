---
name: docs-review
description: "Bring a swarm-routing repository's README, AI files (AGENTS.md, CLAUDE.md, CONTEXT.md) and docs/ to the org documentation standard, which is AntHocNet's: the org-sync badge row, a short explanation of the project, its page on the Colony Arena site, the ns-3 image for ns-3 repos, a layout that matches the tree, Epics, licence and how-to-work-here sections, a docs/ map with no orphan pages and no broken links, and no claim the repository cannot back. Use whenever a README or docs page is written or reviewed in an org repository, a repository is set up or its status changes, someone asks for badges, the game or site link, the container link or a docs cleanup, or before a docs PR. Script first: check_docs.py does the mechanical checks; you judge the prose."
license: MIT OR GPL-2.0-only
compatibility: Needs python3 and network access to github.com (scripts/check-docs clones swarm-routing/.github tools/docs-review).
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# docs-review

The org's documentation standard is AntHocNet's README and docs map. A script
checks what can be checked; whether the explanation reads well, whether the
status is honest and whether Quick start works are yours. Run the script
first.

```bash
SKILL="$CLAUDE_PLUGIN_ROOT/skills/docs-review"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
"$SKILL"/scripts/check-docs .   # in the repository under review; --json for machine output
```

Inside a `swarm-routing/.github` checkout, `python3 -I
tools/docs-review/check_docs.py <repo>` is the same; `ORG_TOOLS_DIR=<checkout>`
points the wrapper at a local one.

## 1. Run the mechanical checks

One line per check, `PASS`, `WARN` or `FAIL`, with the files under it; exit 1
on a FAIL:

| Where | Checked | Level |
|---|---|---|
| README | `# Title` first; the org-sync badge row | FAIL |
| README | an explanation (a paragraph of 2+ sentences) near the top | WARN |
| README | a link to its site page `https://swarm-routing.github.io/arena/<id>/` (AntHocNet: its game); for ns-3 repos, the `ns3-dev` image | WARN |
| README | `## Epics`, a licence section linking LICENSING.md, a link to AGENTS.md or CONTRIBUTING.md | WARN |
| README, AGENTS.md | layout blocks naming directories that do not exist and are not marked planned; README and AGENTS.md status words that disagree | WARN |
| AGENTS.md | the org's sections (What this repo is … Where to look) | FAIL |
| CLAUDE.md | imports `@AGENTS.md` | FAIL |
| CONTEXT.md | still the org-sync seed although the repo has code | WARN |
| docs/ | a `docs/README.md` map once there are two pages; pages linked from nowhere; ADRs missing from `docs/adr/README.md` | WARN |
| links | relative links in README, AGENTS.md, CONTEXT.md and docs/ resolve | FAIL |

A repository tunes it in a `[docs]` table of `.github/org-sync.toml`:
`arena_id` (its id in the site's `projects.json`, default the repo name) and
`uses_image`. Fix every FAIL. Resolve each WARN or explain it in one line.

## 2. Fix through the owner of each part

Some parts of these files are generated. Edit those only through their tool,
or the next run undoes the edit:

- **Badges** (between `<!-- org-sync:begin badges -->` markers) come from
  `badges` in `.github/org-sync.toml`. The site and image links are the
  `arena` and `ns3dev` badges: add the names there and run
  `org_sync.py apply` (the `org-repo` skill). Never type a badge by hand.
- **The org sections of AGENTS.md and CLAUDE.md** (between `org-sync`
  markers) come from `swarm-routing/.github` `templates/`.
- **`## Epics`** comes from `epics.py readme`.

Everything else is the repository's own: the opening paragraph, the layout
blocks, Quick start, CONTEXT.md and docs/.

- **A layout directory that does not exist** is marked planned
  (`(planned, #N)` on its line, or "The layout below is the plan" above the
  block, as the protocol repositories do). Never create an empty directory to
  satisfy the check.
- **An orphan docs page** gets a row in `docs/README.md` (a one-line "what you
  find there"), or is removed if it is obsolete. Say which.
- **A broken link** points at the file that exists now, or the sentence
  changes. Never create a stub file to make a link resolve.

## 3. Judge what the script cannot

Each needs a sentence in the report, even when the answer is "fine":

- **The explanation.** Two or three sentences a newcomer understands: what
  the project is (the protocol and its paper, or the tool), why it exists in
  the org, and its status. Take the facts from AGENTS.md "What this repo is",
  never from memory. The site and image links sit in the opening (the badge
  row), not at the bottom.
- **Honest status.** The README, AGENTS.md and CONTEXT.md give the same
  status, and it matches the tree: no "works", "supports" or "fast" for a
  part that is planned. A number comparing protocols (delivery ratio,
  latency, "beats AODV") needs its run, per-seed paired over at least 20 seeds
  (org rule 6); without one, the sentence goes, and the report says so.
- **Quick start.** The commands match AGENTS.md "Build & verify" and the
  repository's Makefile targets. A command for a part that does not exist yet
  is marked as the plan.
- **CONTEXT.md** states the current state and the next work, with the issue
  numbers (handoff, epic), when the repository has content.
- **docs/README.md** says in one line what each page is for, so a reader picks
  the right one.

## 4. Report

```
check_docs: <last line, e.g. "WARN  review the warnings above">
- fixed: <file: what changed, one line each>
- generated: <badges / org sections / Epics changed through which tool, or "none">
- explained: <each WARN left, and why>
- judgement: explanation <ok / rewritten>; status <consistent / fixed: …>; claims <none unbacked / removed: …>; quick start <matches / fixed>
```

Propose the edits as one PR per repository (a `docs:` title). Do not merge.
