---
name: docs-review
description: "Bring a swarm-routing repository's README, AI files (AGENTS.md, CLAUDE.md, CONTEXT.md) and docs/ to the org documentation standard, which is AntHocNet's: the org-sync badge row, a short explanation of the project, its page on the Colony Arena site, the ns-3 image for ns-3 repos, a layout that matches the tree, Epics, licence and how-to-work-here sections, a released repository's DOI and citing section with the papers it implements, a docs/ map with no orphan pages and no broken links, and no claim the repository cannot back. Use whenever a README or docs page is written or reviewed in an org repository, a repository is set up or its status changes, someone asks for badges, citation or DOI references, the game or site link, the container link or a docs cleanup, before a docs PR, or when handoff lessons or a `[docs] AI files` issue should be folded back into AGENTS.md and CLAUDE.md. Script first: check_docs.py does the mechanical checks; you judge the prose."
license: MIT OR GPL-2.0-only
compatibility: Needs python3 and network access to github.com (scripts/check-docs clones swarm-routing/.github tools/docs-review); step 4 and --online also need the GitHub CLI, logged in (gh auth login) or with GH_TOKEN set.
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
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/docs-review"   # as the Claude Code plugin
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
| citation | a released repository (a `v*` tag or `zenodo_concept`): the DOI badge; CITATION.cff whose `doi:` is the concept; a README section on citing it that links CITATION.cff (AntHocNet's "Releases & citing"); for a protocol, a CITATION.cff reference per source, each with a `doi:` or the reason it has none | FAIL |
| citation | a protocol whose CITATION.cff cites no source; a `v*` tag but no `zenodo_concept` (Zenodo has not archived it yet) | WARN |
| AI files | outside the org-sync sections of AGENTS.md, CLAUDE.md, CONTEXT.md: paths that do not exist; paths marked planned that exist; with `--online`, issues written as open or blocking that are closed; text an org rule replaced (the script's `CONTRADICTIONS` table names each source); checks called required that are not | WARN |

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
  If `org_sync.py plan` does not know those names (an older checkout of the
  org tools), link the site page and the image in the opening paragraph
  instead, and say so in the report.
- **The org sections of AGENTS.md and CLAUDE.md** (between `org-sync`
  markers) come from `swarm-routing/.github` `templates/`.
- **`## Epics`** comes from `epics.py readme`.
- **Citing** (the README's Releases & citing section between
  `<!-- org-sync:begin citing -->` markers, CITATION.cff's `doi:` and
  `references:`, the DOI badge) comes from two places. The repository's own
  record is in `.github/org-sync.toml`: `citation = true`, `zenodo_concept`
  (read from Zenodo, never typed) and `citation_type`. The works it relies
  on are the entries of `docs/references.bib` (its `implemented`, `tool` and
  `dataset` entries reach CITATION.cff's `references:` and the citing list).
  A work that is missing, stale or shown without its DOI link is fixed in
  the bib, never in the README or CITATION.cff: that is the `references`
  skill's job (each entry printed by `fidelity.py bib entry <DOI> --key K
  --role R` from Crossref's record, never typed; `fidelity.py bib check .`
  lists what is wrong). Then, in a repository with `citation = true`, run
  `org_sync.py apply` and `org_sync.py reseed CITATION.cff`; without it
  org-sync renders neither the citing section nor CITATION.cff (`reseed`
  answers "not a seed"), so do not run them: only CITATION.cff's
  `references:` block is updated, as the `references` skill describes, and
  the report says the repository has no `citation = true`. CITATION.cff is a seed and a reseed
  rewrites the whole file: run `org_sync.py seeds` first, and when it says
  the file differs by more than the template's own change (fields added by
  hand, a dataset's message), say so in the report and leave the file to the
  `references` skill instead of reseeding over those fields. A tagged
  repository without `zenodo_concept` waits for Zenodo to archive the
  release; report it, never invent a DOI.

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

## 4. Fold recorded lessons back into the AI files

The AI files are what the next agent reads, so what earlier sessions learned
belongs in them. Two sources say what to change:

```bash
# owner/name of the repository under review, from its origin remote
R=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
# the "Lessons for the AI files" field of recent handoffs (open and closed)
gh api "repos/$R/issues?labels=handoff&state=all&per_page=15" \
  --jq '.[] | "#\(.number) [\(.state)] \(.title)\n\(.body // "" | split("### Lessons for the AI files")[1] // "(no lessons field)" | split("\n### ")[0])"'
# the weekly findings issue (swarm-routing/.github ai-files-review.yml)
gh api --paginate "repos/$R/issues?labels=documentation&state=open&per_page=100" \
  --jq '.[] | select(.title | startswith("[docs] AI files:")) | "#\(.number) \(.title)\n\(.body)"'
"$SKILL"/scripts/check-docs . --online   # the same findings, now
```

`--online` and the AI-files rows need the org tools at or after
swarm-routing/.github#146; with an older `ORG_TOOLS_DIR` or `ORG_TOOLS_REF`
the script rejects the flag, so update that checkout first. If `gh` reports
it is not logged in, run `gh auth login` (or set `GH_TOKEN`) and repeat; never
skip the step silently.

Sort every lesson and finding into one of four, and say which in the report:

- **An org rule** (every repository should know it): a PR to
  `swarm-routing/.github` changing `templates/agents/` (and CONTRIBUTING.md
  where the rule lives), so org-sync renders it everywhere. Never paste an org
  rule into one repository's hand-written section.
- **A local fact** (true of this repository only): fix it in this repository's
  own sections of AGENTS.md, CLAUDE.md or CONTEXT.md, together with the
  checker's findings, in one PR, `docs(agents): fix stale facts in the ai
  files`. A managed section changes only through `templates/`.
- **Stale text the checker flags as contradicting an org rule** (its
  `CONTRADICTIONS` table names the rule and its source): the org rule already
  decided it, so correct the repository's text in the same `docs(agents)` PR.
- **A change to a rule** (a lesson that says an existing rule, org or local,
  should change): a maintainer decision. List it on the findings issue or the
  handoff with the evidence; do not change the rule.

A lesson already in the AI files needs nothing. Link the handoff issue the
lesson came from in the PR body.

## 5. Report

```
check_docs: <last line, e.g. "WARN  review the warnings above">
- fixed: <file: what changed, one line each>
- generated: <badges / org sections / Epics changed through which tool, or "none">
- explained: <each WARN left, and why>
- judgement: explanation <ok / rewritten>; status <consistent / fixed: …>; claims <none unbacked / removed: …>; quick start <matches / fixed>
- lessons: <handoff #N: org rule → .github PR / local fact → this PR / decision → listed on #M; or "none recorded">
```

Propose the edits as one PR per repository (a `docs:` title), and one
`swarm-routing/.github` PR for org rules. Do not merge.
