---
name: dependency-bump
description: "Check or bump how a swarm-routing repository builds on another org repository's release: swarm-core.lock (or another release lock such as AntHocNet's ns3-tools.lock), the places that name its tag or commit (Makefile, core-deps, the ns-3 CI's dependencies, a benchmark cell), and the `swarm-core / pin` check. Use whenever `swarm-core / pin` is red, a swarm-core or ns3-tools release is out, org-bot's `org-bot/swarm-core-pin` PR needs handling, someone asks which release a repository builds on, or a diff edits a lock. Script first: release_lock.py and check-swarm-core-pin.py read every value from the release; you never type a tag, commit or hash."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 3.10+ and network access to github.com (scripts/org-tool clones swarm-routing/.github tools/checks; the checks read tags with git ls-remote and the release's SHA256SUMS). gh for reading PRs.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# dependency-bump

A protocol repository builds on a **release** of its dependency, never on a
moving ref (swarm-routing/.github CONTRIBUTING "Dependencies"). The release is
named in one file, a lock (`swarm-core.lock`: `SWARM_CORE_REPO`, `_TAG`,
`_COMMIT`, `_VERSION`, `_ASSET`, `_SHA256`), and repeated in a few places the
check ties to it: the `Makefile` and the ns-3 CI's `dependencies:` name the
tag; `core-deps` and a benchmark cell's `dependencies:` name the commit the
tag names; `canary-dependencies:` alone names `@main`. Every value is read
from the release by a script. A hand-typed hash is the one way to get this
wrong, so you never write one.

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/dependency-bump"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
T="$SKILL/scripts/org-tool"    # T release-lock|swarm-core-pin ...
```

Run every command from the consumer's checkout root (the lock is given as a
path below the current directory). `ORG_TOOLS_DIR=<checkout of
swarm-routing/.github>` points the wrapper at a local one.

## 1. Read the state

```bash
"$T" swarm-core-pin                          # the `swarm-core / pin` check, exactly as CI runs it
"$T" release-lock verify swarm-core.lock     # the lock against its release: tag -> commit, the asset's SHA256
"$T" release-lock latest swarm-core.lock     # locked vs newest release: current, or behind
```

| What it prints | Meaning | Next |
|---|---|---|
| `ok, swarm-core.lock names vX, the newest swarm-core release` | current | nothing to do |
| a newer release than the lock | the pin check is red on every PR here | step 2 |
| a place that names another tag or commit than the lock | a hand edit drifted | step 3, `--bump` rewrites the pin lines |
| `does not verify` (tag moved, hash differs) | the lock is wrong or the release was replaced | stop and report: never re-hash to make it pass |
| no `swarm-core.lock`, `SWARM_CORE_REF` commit pin | the old pin mode | step 4 |

For another lock (AntHocNet's `ns3-tools.lock`, prefix `NS3_TOOLS`), `verify`
and `latest` work the same; `swarm-core-pin` is only for swarm-core.

## 2. A newer release is out: org-bot's PR first

org-bot's `swarm-core-pin` task opens one PR per repository once the pin
check is red: head `org-bot/swarm-core-pin`, title `chore(core): bump the
swarm-core pin (org-bot)`. Look for it before doing anything:

```bash
gh api "repos/swarm-routing/<repo>/pulls?state=open&per_page=100" \
    --jq '.[] | select(.head.ref == "org-bot/swarm-core-pin") | "#\(.number) \(.title)"'
```

If it exists, shepherd it (the `pr-shepherd` skill): never push to an
`org-bot/*` or `bot/*` branch, and never open a second bump beside it. If it
is red on `check / org-sync` while a template refresh is red on `swarm-core /
pin`, the two block each other (swarm-routing/.github#429): `pr-shepherd`
says what to report and the one combined PR that clears it, only when the
user asks. Every other PR in the repository waits on this one, so it lands
first.

## 3. No bot PR, and the user asked for the bump

From a branch off `origin/main` (`claude/swarm-core-vX.Y.Z`):

```bash
"$T" swarm-core-pin --bump                   # writes the lock from the release, moves tag and commit on the pin lines only
"$T" release-lock verify swarm-core.lock     # must say verifies
"$T" swarm-core-pin                          # must say ok
make core-test                               # core/ on the new release (and `make test` where ns3/ exists)
git diff --stat                              # the lock, Makefile, workflows; nothing else
```

`--bump` leaves recorded data alone (a `##PROV##` line, a campaign plan, a
doc naming the old commit records what a run used, swarm-routing/.github#407).
If the diff touches anything else, stop. A core test that fails on the new
release is a finding for that repository (an issue, with the failing test),
not a reason to keep the old lock silently. Title: `chore(core): bump
swarm-core to vX.Y.Z`; the body pastes the three check lines.

A lock org-bot does not bump (`ns3-tools.lock`) is a hand PR the same way,
written by `render` (the asset name as the lock's comment and the
repository's docs give it), then `verify`:

```bash
"$T" release-lock render --prefix NS3_TOOLS --repo swarm-routing/ns3-tools \
    --tag "$(gh api repos/swarm-routing/ns3-tools/releases/latest --jq .tag_name)" \
    --asset '<asset name>' > lock.new
```

`render` prints one `<P>_SHA256` for `--asset`; a lock with several asset
hashes (`ROUTING_BENCH_SHA256`, `NS3_TOOL_WHEEL_SHA256`) keeps its key
names, each hash read from that release's `SHA256SUMS`, and its own
`verify` tool (`tools/ns3_tools.py verify` in AntHocNet) must pass. Keep the
lock's header comment.

## 4. A repository still on a commit pin

Every protocol repository consumes swarm-core by its lock since swarm-core
v0.3.0 (ARA, BeeAdHoc, Termite, HOPNET, AntHocNet), and a new one starts with
the lock (the `ns3-new-module` skill, #12). If `swarm-core-pin` reports the
commit-pin mode anyway, there is no script for the switch yet: report it and
point to CONTRIBUTING "Dependencies" (the switch paragraph); do not hand-edit
the build to a lock from this skill.

## Rules

- Never type a tag, commit, version or hash: `render` and `--bump` write
  them; `verify` proves them.
- Never point a committed build at a branch or an unreleased commit. Work
  against unreleased swarm-core with `-DSWARM_CORE_DIR=<checkout>/core`
  locally; it lands after a release.
- Never loosen `moving_refs`, the pin check or a required check to get a PR
  through.

## Report

```
<repo>: locks <tag> (newest <tag>) · pin check <ok|red: reason>
action: <none | shepherding org-bot #N | bump PR #N | switch PR #N>
checks: verify <line> · swarm-core-pin <line> · core tests <pass|fail: test>
```
