# Developer guide

This repository holds the org's agent skills: each `skills/<name>/` is a
`SKILL.md` procedure (in the [Agent Skills](https://agentskills.io/specification)
format) with thin wrapper scripts and test cases, published both as the
Claude Code plugin `swarm-routing` and through skills.sh. The scripts that do
the work live in swarm-routing/.github `tools/` (or this repository's
`tools/`). This page shows how to set up, test, lint and try a skill, and
what CI checks. The README's "Add a skill" is the step-by-step for a new
skill; the rules (notably golden rule 10: this repository is a trust
boundary) are in [AGENTS.md](../AGENTS.md); how issues and pull requests work
is in the org's
[CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md).

## Prerequisites

| Tool | Version | Needed for |
| --- | --- | --- |
| Linux or macOS, `git`, `make`, `bash` | any recent | everything |
| Python | 3.11 or newer | the checks and tools (standard library only) |
| actionlint | 1.7.12 (`pip install actionlint-py==1.7.12.25`) | `make lint` |
| shellcheck | 0.10 (`pip install shellcheck-py==0.10.0.1`) | the wrapper and grader scripts |
| ruff | 0.17.1 | Python lint and format |
| Docker with its daemon running, or Go | Docker: any recent; Go: 1.27 (swarm-routing/.github `go.mod`) | `make headers`: the licence gate CI runs, from the ci-tools image, or built with `go` when docker is absent |
| Claude Code (`claude`) | current | optional: `claude plugin validate .`, trying a skill as a plugin |
| Node.js with `npx` | 18 or newer | optional: trying the skills.sh install |

## Get the code

```bash
git clone https://github.com/swarm-routing/skills.git
git clone https://github.com/swarm-routing/.github.git   # most skills wrap its tools/
cd skills
```

There are no submodules. The wrappers fetch swarm-routing/.github on their
own when run; set `ORG_TOOLS_DIR=../.github` to use your checkout instead
(needed to test a change to a tool before it merges).

## Dependencies

None to install: the checks use the Python standard library, and each
skill's script comes from swarm-routing/.github at `main` (or
`ORG_TOOLS_DIR`/`ORG_TOOLS_REF`). The release locks and the vcpkg plan
(swarm-routing/.github#489) do not apply here.

## Build

Nothing compiles (`make build` says so). The plugin is the repository
itself: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`,
with the skills under `skills/`.

## Test

| What | Command | CI |
| --- | --- | --- |
| manifests and every skill against the spec, the wrappers' cache block, the eval grader and token-audit self-tests | `make test` | `plugins` |
| Claude Code's own plugin check | `claude plugin validate .` | (local only) |
| the Python tests with coverage | each of `tools/checks/test_check_plugins.py`, `tools/evals/test_grade.py`, `tools/token-audit/test_token_audit.py`, `tools/tracker-responses/test_responses.py` with `python3 -I` | `python / python` |
| a skill's eval workspace, script graders | `ORG_TOOLS_DIR=../.github python3 tools/evals/grade.py <skill>-workspace/iteration-N [--write]` | (local only) |

`make test` ends with `check-plugins: 0 problem(s)` and each self-test's
`ok` line.

## Run

Run a skill's script the way the skill does, from the repository it
reviews, for example the docs check:

```bash
ORG_TOOLS_DIR=../.github skills/docs-review/scripts/check-docs /path/to/a/repository
python3 -I tools/token-audit/token_audit.py files .   # what a session loads from this repository's agent files
```

To try the skills in Claude Code, install the plugin from a local path or
from GitHub (README "Install"); with skills.sh, `npx skills add
swarm-routing/skills --skill <name>`. The plugin follows `main`, so a
change reaches sessions once it merges and the marketplace refreshes.

## Docker and dev containers

Nothing here needs Docker. `make shell` opens a shell in `python:3.13-slim`
with this checkout at `/src`, if you want a clean Python. There is no
`.devcontainer/`.

## Lint and format

```bash
make lint      # actionlint
find skills \( -path '*/scripts/*' -o -path '*/graders/*.sh' \) -type f -print0 | xargs -0 -r shellcheck
ruff check tools && ruff format --check tools   # as python / python, with the org's ruff.toml
make headers   # licence headers (fetches the org tools)
make org-sync-check
make check     # lint, test, headers and org-sync together
```

## CI map

| Workflow | Job (check name) | What it checks | Required |
| --- | --- | --- | --- |
| `ci.yml` | `plugins` | `make test`; actionlint; shellcheck on the wrappers and script graders | yes |
| `ci.yml` | `python / python` | ruff and the Python tests with coverage | yes |
| `licence.yml` | `headers / licence` | licence headers | yes |
| `org-sync.yml` | `check / org-sync` | the org-managed files match the templates | yes |
| `pr-title.yml` | `title / title` | the PR title is a lowercase Conventional Commit | yes |
| `review-gate.yml` | `review / coderabbit` | CodeRabbit has reviewed the PR | yes |
| `dco.yml`, `scorecard.yml`, `sync-labels.yml` | | sign-off on outside contributions; OpenSSF Scorecard; labels | no |

The required checks are the ones the `main` ruleset lists: `gh api
repos/swarm-routing/skills/rules/branches/main`. `main` merges through a
merge queue, so a pull request is merged by enabling auto-merge.

## Release

The plugin follows `main`, and versioned releases are cut on the
maintainer's request only (swarm-routing/.github#636). Every change to the
plugin bumps its version in `.claude-plugin/plugin.json`, its entry in
`.claude-plugin/marketplace.json`, `.cz.toml` and `CITATION.cff` together,
in the same PR (golden rule 12; `make test` checks they match), so Claude
Code sees the update. A release (`.github/workflows/release.yml`, on
swarm-routing/.github's `reusable-release.yml`) bumps all four with
Commitizen and tags that version; the first tag continues from 0.32.x
(`first-release-from-config`), not 0.1.0. `make dist` writes its asset,
`dist/skills-<version>.tar.gz` (the tree at `HEAD`). The ladder is
[`docs/roadmap.md`](roadmap.md); the procedure is
[CONTRIBUTING "Cutting a release"](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#cutting-a-release).

## Troubleshooting

- **`check-plugins` says a description is too long.** The spec caps it at
  1024 characters; shorten it.
- **`check-plugins` says the versions differ.** Bump `plugin.json`, the
  marketplace entry, `.cz.toml` and `CITATION.cff` together.
- **`check-plugins` says a cached-checkout block differs.** A wrapper that
  fetches a repository copies that block unchanged from an existing wrapper.
- **A wrapper runs an older version of a tool.** It fetches swarm-routing/.github
  `main`; set `ORG_TOOLS_DIR` to your checkout to test an unmerged change.
- **Claude Code does not offer a new skill.** Run
  `claude plugin marketplace update swarm-routing` and start a new session.
- **A skill tells an agent to change permissions, weaken a check or send
  data anywhere.** That is never allowed here (golden rule 10), whatever the
  task.
