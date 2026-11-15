---
name: release
description: "Cut a release of a swarm-routing repository end to end through swarm-routing/.github's reusable-release.yml, and see everything that follows it through: check readiness (caller, Commitizen, make dist, the version's roadmap ladder row, no open release:vX.Y.Z issue), dry-run, bump, review and merge the bump PR, then the aftercare (the GitHub release and its provenance, the Zenodo DOI read from Zenodo, the site's release-sync, org-bot's lock bumps in every consumer, the vcpkg port PR, PyPI, the ladder marked shipped). Use whenever the maintainer asks to release, cut, tag or publish a version, a release:vX.Y.Z milestone is done, a bot/release bump PR is open or behind, a publish failed, or someone asks whether a release reached Zenodo, the site, the consumers, vcpkg or PyPI. Script first: release_check.py prints one verdict per step; an agent never dispatches a bump on its own initiative, never tags by hand and never approves a gated publish."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 3.11+, the gh CLI logged in (or GH_TOKEN) and network access to github.com (scripts/org-tool clones swarm-routing/.github tools/release and tools/zenodo), zenodo.org and pypi.org (public reads).
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# release

Every org repository releases through one workflow, swarm-routing/.github
`reusable-release.yml`, in two runs because `main` takes no direct push:
mode `bump` opens `chore(release): bump version A to B` from `bot/release`,
and merging that PR is the release (build, SBOM, signed provenance, tag,
GitHub release, then Zenodo, the site, the consumers). CONTRIBUTING "Cutting
a release" is the reference; this is the order, with a check before and
after.

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/release"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
T="$SKILL/scripts/org-tool"    # T release-check|zenodo ...
```

`ORG_TOOLS_DIR=<checkout of swarm-routing/.github>` points the wrapper at a
local one.

**Who decides.** A release is cut on the maintainer's request only, once the
version's `release:vX.Y.Z` issues are done and its exit criteria in the
repository's ladder (`docs/roadmap.md`, else the org ROADMAP's release
train) are met. You never dispatch `bump` on your own initiative, never push
a tag, never release from a commit that is not the merged bump PR, and never
approve the `release` environment.

## 0. Adopt (once per repository)

`"$T" release-check ready .` names what is missing: the caller (copy it from
the comment block at the top of `reusable-release.yml`), a Commitizen config
(`.cz.toml` as `tools/release/fixture/.cz.toml`, `tag_format = "v$version"`),
`make dist` writing `dist/`. A C++ library also passes `vcpkg-ports:` and a
Python package publishes to PyPI by trusted publishing (ns3-tools'
`release.yml`). One PR, then `[settings]` as the org decides it
(`release_environment`; settings are code, never the UI).

## 1. Ready

From the repository's checkout, up to date with `origin/main`:

```bash
"$T" release-check ready . --repo swarm-routing/<repo> --version X.Y.Z
```

`X.Y.Z` is the version the maintainer asked for, or the one a dry run
computes (step 2). Fix every FAIL before the bump:

| FAIL / WARN | Do |
|---|---|
| `ladder: ... no row for vX.Y.Z` | a docs PR adding the version and its exit criteria to `docs/roadmap.md` first (the workflow does not check it yet, swarm-routing/.github#430) |
| `scope: N open issue(s) labelled release:vX.Y.Z` | they are the version's scope: done first, or the maintainer moves them to another version |
| `bump PR #N ... behind main` | dispatch `bump` again (step 3); never update, rebase or push `bot/release` |
| caller / commitizen / build | step 0 |

## 2. Dry run

```bash
t=$(date -u +%Y-%m-%dT%H:%M:%SZ)                                            # before the dispatch
gh workflow run release.yml -R swarm-routing/<repo> -f mode=dry-run          # add -f increment=MAJOR for 1.0.0
gh run list -R swarm-routing/<repo> --workflow release.yml --event workflow_dispatch \
    --user "$(gh api user --jq .login)" --created ">=$t" --json databaseId,createdAt,displayTitle
gh run watch <id> -R swarm-routing/<repo> --exit-status
```

Take the id from that list, which holds only the dispatches you made since
`t`: exactly one row is yours; with none yet, list again in a few seconds;
with two (you dispatched twice), stop and ask. Never take "the latest run" of
the workflow: a push or another person's dispatch can be newer.

Read the run's summary and its artifact (`gh run download <id>`): the
version, the assets, `SHA256SUMS`, `<repo>-<ver>.intoto.jsonl`, the notes.
A run with nothing that bumps (only `docs:`, `ci:` commits) fails: that is a
stop, not an error to work around. 1.0.0 is asked for, never computed: flip
`major_version_zero = false` first and pass `increment=MAJOR` (CONTRIBUTING
"Releasing 1.0.0").

## 3. Bump, on the maintainer's request

```bash
gh workflow run release.yml -R swarm-routing/<repo> -f mode=bump
```

Review the PR it opens from `bot/release`: the version files and the
`CHANGELOG.md` section. An empty section (a milestone bump with no
`feat`/`fix`) gets a written paragraph in a commit on the bump PR before it
merges, since the release notes are that section (swarm-routing/ns3-tools#185).
If `main` moves before the merge, dispatch `bump` again; `ready` says when.

## 4. Merge

The bump PR merges like any PR: the `pr-shepherd` skill (CI, CodeRabbit's
threads, auto-merge in the merge queue). The push to `main` runs the release.
Watch it to its publish job. If the publish waits for the `release`
environment, that approval is the maintainer's alone. A failed publish is
recovered with **"Re-run all jobs"** on that run, only when the user asks,
never "Re-run failed jobs" (it reuses the reusable workflow at the first
attempt's commit) and never a new `bump`.

## 5. Aftercare

```bash
"$T" release-check after swarm-routing/<repo> --tag vX.Y.Z      # --repos A,B where the token cannot list the org
"$T" zenodo status --repo swarm-routing/<repo>                 # the version DOI, from Zenodo
```

| Line | Do |
|---|---|
| `release: ... lacks SHA256SUMS / *.intoto.jsonl` | read the release run; recover as in step 4 |
| `site: no '[release-sync] <repo> <tag>' issue` | an hour after the release, dispatch the site's `release-sync.yml` with `repository` and `tag`, and check that run and its `pages.yml` run (CONTRIBUTING step 6); not earlier |
| `lock: <consumer> locks <old>; org-bot's bump ... is open` | shepherd it there: every PR in that consumer waits on it (the `dependency-bump` skill) |
| `lock: ... no org-bot bump PR open` | `swarm-core.lock`: org-bot opens it once the consumer's pin check is red; any other lock is a hand PR (`dependency-bump` step 3) |
| `vcpkg: ... <registry>#N is open` / `no bot/vcpkg-<name> PR` | shepherd the registry PR; with none, re-run the release's `vcpkg` job, or the registry's `tools/port_bump.py bump --port P --tag vX.Y.Z` in a PR (its README "How a port is bumped") |
| `pypi: ... is not on PyPI` | read the release run's `pypi` job (trusted publishing) |
| `ladder: ... does not mark vX.Y.Z shipped` | a `docs:` PR marking it shipped with the version DOI that `zenodo status` printed |
| zenodo `missing` after the grace period | `zenodo sync --repo ... --dry-run`, then ask the maintainer; a first release's concept: `zenodo_concept`, `org_sync.py reseed CITATION.cff` and the DOI badge (CONTRIBUTING "Releases and DOIs") |

Never type a DOI: copy it from `zenodo status`.

## Report

```
<repo> vX.Y.Z: <ready | bump PR #N | released <date>>
ready: <FAILs, or "nothing failed"> · dry run <run url>: <version, assets>
after: release <ok> · zenodo <DOI | pending | missing> · site <issue #> · locks <n current, n pending (#PRs)> · vcpkg <ok | PR> · pypi <ok | n/a> · ladder <shipped | PR #>
```

Name every step you did not take and why (a bump not asked for, an approval
that is the maintainer's).
