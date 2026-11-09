---
name: org-repo
description: Set up a new swarm-routing repository, or update an existing one, from the org templates — README badge row, AGENTS.md/CLAUDE.md org sections, CONTEXT.md, docs/adr, LICENSE/LICENSING.md, SECURITY.md, the standard Makefile targets, the org-sync CI check and the marketplace keys of .claude/settings.json. Use when bootstrapping an org repo, when its org-sync check is red, or when an org template changed and repos need the update. Script first: run tools/org-sync and read its summaries, never the files.
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/org-sync clones swarm-routing/.github tools/org-sync).
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# org-repo

Every action is a `tools/org-sync` command from `swarm-routing/.github`; this
skill only orders them and says where judgement is needed. `scripts/org-sync`
(next to this file) runs it from a cached clone; inside a checkout of
`swarm-routing/.github`, `python3 tools/org-sync/org_sync.py` is the same.

Read the command output only. Do not open the managed files to "check": the
summary says what changed, and `conflicts` shows the only hunks that need
you.

## 1. Mode

- **init**: the repo has no `.github/org-sync.toml`. Pick the kind from what
  the repo ships: `protocol` (ns-3 module + core), `c-cpp`, `python`,
  `container`, `data`, `site`, `skills`. If it is not obvious, ask once.
  Then `scripts/org-sync init . --kind KIND [--dual core/ tools/]`
  (`--dual ''` when the whole repo is tooling). Edit the new
  `.github/org-sync.toml` for `description`, `trust_boundary`,
  `limitations`, `verifying` (and `image`, `docs_url`, `cxx`, `python`,
  `module` where they apply) before the next step; write no claim the repo
  cannot back.
- **update**: the file exists. Go to 2.

## 2. Plan, apply, resolve, check

```bash
scripts/org-sync plan --json .   # {"unchanged":N,"changes":[{item,status,lines,detail}]}
scripts/org-sync apply .          # one line per written item; conflicts listed, not written
scripts/org-sync conflicts .      # only when apply listed a conflict: the hunks, 3 lines of context
scripts/org-sync check .          # must print "org-sync: in sync"
```

Statuses: `create`, `update` (a managed part differs from the template),
`adopt` (markers added around text already equal to the template),
`conflict`, `unchanged`.

**Conflicts are the only judgement step.**
- A managed section whose text differs from the template: if the difference
  is repo-specific, move it **outside** the markers (for example a repo rule
  goes after rule 9 as rule 10), then rerun `apply`; if it is just stale,
  `scripts/org-sync apply . --force ITEM`.
- No marker and nothing to adopt: add the two marker lines
  (`<!-- org-sync:begin NAME -->` / `<!-- org-sync:end NAME -->`) where the
  section belongs and rerun `apply`.
- `Makefile#targets` missing a target: add that target with this repo's
  command (the Makefile is the repo's own; only the names are checked).

## 3. Settings the files cannot hold

`scripts/org-sync settings .` reports private vulnerability reporting, merge
methods and rulesets (`have` / `want`). Change nothing yourself: list every
`have != want` row in the PR body as a checklist for an admin.

## 4. Pull request

One PR to `main` with a Conventional Commit title, e.g.
`chore: adopt the org templates (org-sync)`, body in the org PR template:
what `apply` printed, the conflicts and how each was resolved, the
`settings` checklist, and anything that could not be applied (a badge whose
target does not exist yet). CI runs the same `check` through
`reusable-org-sync-check.yml`.
