---
name: org-repo
description: "Set up a new swarm-routing repository, or update an existing one, from the org templates — README badge row, AGENTS.md/CLAUDE.md org sections, CONTEXT.md, docs/adr, LICENSE/LICENSING.md, SECURITY.md, the standard Makefile targets, the org-sync CI check and the marketplace keys of .claude/settings.json. Use when bootstrapping an org repo, when its org-sync check is red, or when an org template changed and repos need the update. Script first: run tools/org-sync and read its summaries, never the files."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/org-sync clones swarm-routing/.github tools/org-sync).
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# org-repo

Every action is a `tools/org-sync` command from `swarm-routing/.github`; this
skill only orders them and says where judgement is needed. `scripts/org-sync`
(next to this file) runs it from a cached snapshot; inside a checkout of
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
`conflict`, `orphan` (an `org-sync:begin NAME` / `org-sync:end NAME` block
in a managed file whose section is not one of this repository's items),
`unchanged`.

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

**An orphan** is left by `apply`, reported, and keeps `check` red, like a
conflict. Its detail line gives the two ways out; which one is right depends
on whether the repository should have that section:
- it should not (the section is skipped in `.github/org-sync.toml`, or its
  item is not enabled, on purpose): `scripts/org-sync apply . --prune-orphans`
  removes the block, markers and text. Say in the PR which block went.
- it should (the skip or the missing opt-in is the mistake): fix the config
  as the detail says ("drop the skip" or "enable its item") and rerun
  `apply`; the block is then a managed section again.
If you cannot tell which, ask; do not prune text someone may have meant to
keep.

## 3. Settings are code, and not this skill's to apply

A repository's GitHub settings (description, topics, the ruleset profile,
required checks, the merge queue, security features) are declared in the
`[settings]` table of its own `.github/org-sync.toml`; org-sync ignores that
table. `swarm-routing/.github` `tools/repo-settings/repo_settings.py` reads
it: its `plan` lists the differences between the live repository and its
declaration and writes nothing. `scripts/org-sync` does not run that tool;
run it from a checkout of `swarm-routing/.github` (needs `gh` logged in, or
`GH_TOKEN`), with the repository's name in place of `ARA`:

```bash
python3 -I tools/repo-settings/repo_settings.py plan ARA
```

Without such a checkout, say in the PR that `plan` was not run.

- A setting that should change is a change to `[settings]` in a reviewed PR
  (a ruleset profile or the Actions allowlist: a PR to `templates/rulesets/`
  in `swarm-routing/.github`). It takes effect when the maintainers'
  `repo-settings` workflow applies it after the merge.
- Never change a setting from the session: not in the UI, not with a direct
  API write, and do not run `repo_settings.py apply`. Do not ask an admin to
  click through a list either; the table is the request.
- In the PR body, name any `[settings]` change the PR makes, and any
  difference `plan` printed that the PR does not address.

A `repo-settings` skill is planned (swarm-routing/skills#44); until then
this is the whole procedure. `scripts/org-sync settings .` still prints four
live values and the ruleset count (`have` / `want`), for information only.

## 4. Pull request

One PR to `main` with a Conventional Commit title, e.g.
`chore: adopt the org templates (org-sync)`, body in the org PR template:
what `apply` printed, the conflicts and orphans and how each was resolved,
the `[settings]` changes (step 3), and anything that could not be applied (a badge whose
target does not exist yet). CI runs the same `check` through
`reusable-org-sync-check.yml`. On a PR the check fails only on drift the PR
itself introduces; drift already on `main` is a warning
(swarm-routing/.github#206), so fix that in its own PR.

## 5. Citation, badges and Zenodo

Every public repository releases and is archived on Zenodo
(swarm-routing/.github#216). Set these before step 2 (or rerun `apply` and
`check` after setting them): the flags alone write nothing. In
`.github/org-sync.toml`, top level:

- `citation = true` seeds `CITATION.cff` (the `cite` badge follows it); add
  `"CITATION.cff:^version:"` to the Commitizen `version_files` so each bump
  keeps its version current.
- The `release` badge appears once a workflow calls `reusable-release.yml`.
- `docs/references.bib` is seeded in every repository (a commented header,
  no entry): it is the repository's one bibliography. Once it holds an
  entry and `citation = true` is set, `CITATION.cff`'s `references:` and the
  README's Releases & citing list are rendered from it (its `implemented`,
  `tool` and `dataset` entries), not from the config. Without
  `citation = true` org-sync renders neither; the repository keeps its own
  README citing section and `CITATION.cff`. Never type an entry: filling and checking
  the bib is the `references` skill (`fidelity.py bib entry <DOI> --key K
  --role R` in `swarm-routing/.github` prints one from Crossref's record).
- After the first release is archived, read the concept record from Zenodo
  (`zenodo.py status --repo swarm-routing/<repo>` in `swarm-routing/.github`,
  or the record's page), never from memory, and set
  `zenodo_concept = "<record id>"`, and run `apply` and `check` again for the
  `doi` badge. `CITATION.cff` is the repository's once seeded: `scripts/org-sync
  reseed CITATION.cff .` prints the diff and rewrites the whole file from
  today's template, so use it only while the file is still the seed
  (`scripts/org-sync seeds .` prints `same`, `differs (N lines)` or
  `missing` for each seed; a `differs` larger than the template's own change
  means fields were added by hand); if the
  repository has added authors or other fields, add the `doi:` line by hand
  instead. One PR, `docs: the zenodo doi badge and citation`.

A release itself is not this skill's job: it is cut only when the maintainer
asks, once the issues labelled with that version (`release:vX.Y.Z`, the
repository's `docs/roadmap.md` ladder) are done, by dispatching the release
workflow's `bump` (CONTRIBUTING "Cutting a release"; a `release` skill is
planned, swarm-routing/skills#43).
