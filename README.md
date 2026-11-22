# skills

<!-- org-sync:begin badges -->
| Group | Badges |
| --- | --- |
| Build | [![CI](https://github.com/swarm-routing/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/swarm-routing/skills/actions/workflows/ci.yml) |
| Release | [![Release](https://img.shields.io/github/v/release/swarm-routing/skills?sort=semver&cacheSeconds=1800)](https://github.com/swarm-routing/skills/releases) [![Cite](https://img.shields.io/badge/cite-CITATION.cff-blue)](CITATION.cff) [![Licence: MIT OR GPL-2.0-only](https://img.shields.io/badge/licence-MIT%20OR%20GPL--2.0--only-blue)](LICENSING.md) |
| Trust | [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/swarm-routing/skills/badge)](https://scorecard.dev/viewer/?uri=github.com/swarm-routing/skills) [![OpenSSF Best Practices](https://www.bestpractices.dev/projects/16823/badge)](https://www.bestpractices.dev/projects/16823) |
| Community & docs | [![Open RCAPA](https://img.shields.io/github/issues/swarm-routing/skills/rcapa?label=open%20RCAPA&color=blue)](https://github.com/swarm-routing/skills/blob/main/docs/rcapa/README.md) [![Claude Code plugins](https://img.shields.io/badge/Claude%20Code-plugin%20marketplace-blueviolet)](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow)](https://www.conventionalcommits.org) [![skills.sh](https://img.shields.io/badge/skills.sh-npx%20skills%20add%20swarm--routing%2Fskills-black)](https://skills.sh) |
<!-- org-sync:end badges -->

The swarm-routing org's **agent skills**, published two ways from one tree:
as the Claude Code plugin **`swarm-routing`**, and as plain
[Agent Skills](https://agentskills.io/specification) that
[skills.sh](https://skills.sh) installs into any agent (Claude Code, Codex,
Cursor, Copilot, …). Each skill is a procedure over a script in
[`swarm-routing/.github`](https://github.com/swarm-routing/.github) `tools/`,
so the script does the work and the skill says when and in what order.

| Skill | What it does | Script |
|-------|--------------|--------|
| [`org-repo`](skills/org-repo/SKILL.md) | set up or update a repo from the org templates: plan, apply, resolve conflicts, check, open the PR | `tools/org-sync/org_sync.py` |
| [`fidelity-sheet`](skills/fidelity-sheet/SKILL.md) | write or check a protocol's paper-fidelity sheet (`docs/fidelity.md`): every mechanism and parameter sourced to the paper, or marked repo choice / unknown; the anchor candidate | `tools/fidelity/fidelity.py` |
| [`protocol-review`](skills/protocol-review/SKILL.md) | review a protocol or tool diff against the org golden rules before a PR: the mechanical checks by script, then wire formats, determinism, paired comparisons and bounded structures by judgement | `tools/protocol-review/check_invariants.py` |
| [`docs-review`](skills/docs-review/SKILL.md) | bring a repository's README, AI files and docs/ to the org standard (AntHocNet's): badges, an explanation, the site page and the ns-3 image, a layout that matches the tree, a docs map, no broken links, no unbacked claims | `tools/docs-review/check_docs.py` |
| [`pr-shepherd`](skills/pr-shepherd/SKILL.md) | take open PRs from review to merge: one line per PR and per unresolved finding, each finding verified then fixed (test first) or declined with a reason, every thread replied to and resolved, merged only when CI is green, no thread is open and the user asked, in dependency order | `tools/pr-status/pr_status.py` |
| [`lit-search`](skills/lit-search/SKILL.md) | find new papers (who cites a paper, its references, a narrow search, related work as a last resort) and confirm a reference field by field against Crossref, Semantic Scholar and OpenAlex, or a thesis without a DOI; free sources only, no key needed | `tools/lit-search/lit_search.py` |
| [`references`](skills/references/SKILL.md) | review and set up a repository's `docs/references.bib`: what it cites, each work confirmed from Crossref or Zenodo, DOI links first, the fidelity Sources table and `CITATION.cff` references regenerated and checked (swarm-routing/.github#307) | `tools/fidelity/fidelity.py`, `tools/lit-search/lit_search.py`, `tools/zenodo/zenodo.py` |
| [`token-audit`](skills/token-audit/SKILL.md) | measure and cut what a session costs in tokens: what it loads before its first tool call (agent files by section, org-managed and repeated text, a budget as a gate; estimates), and where a finished session's tokens went (the first request's context, calls and result bytes per tool, candidates for a script; measured) | this repository's `tools/token-audit/token_audit.py` |
| [`bestpractices`](skills/bestpractices/SKILL.md) | the OpenSSF Best Practices badge (bestpractices.dev): register a repository, propose its passing answers from evidence on `main` (`.bestpractices.json` or proposal links the maintainer reviews and saves; nothing logs in), keep them current with the weekly drift check, and answer one pasted criterion with a paste-ready justification; owner-only criteria stay the maintainer's | swarm-routing/.github `cmd/bestpractices` (Go); this repository's `tools/tracker-responses/responses.py` (tracker counts) |
| [`dependency-bump`](skills/dependency-bump/SKILL.md) | check or bump the release a repository builds on from another org repository: the release lock (`swarm-core.lock`, `ns3-tools.lock`), the places that name its tag or commit, the `swarm-core / pin` check; org-bot's bump PR first, every value read from the release, never typed | `tools/checks/release_lock.py`, `tools/checks/check-swarm-core-pin.py` |
| [`release`](skills/release/SKILL.md) | cut a release end to end on the maintainer's request: readiness (caller, Commitizen, `make dist`, the version's ladder row, no open `release:vX.Y.Z` issue, a behind bump PR), dry-run, bump, merge, then the aftercare (provenance, the Zenodo DOI read from Zenodo, the site's release-sync, consumers' lock bumps, the vcpkg port, PyPI, the ladder marked shipped) | `tools/release/release_check.py`, `tools/zenodo/zenodo.py` |
| [`sonar-triage`](skills/sonar-triage/SKILL.md) | record a reviewed SonarQube Cloud finding as a false positive or an accepted wontfix: review the code, list the findings and print the entry from the API, add it to `decisions.toml`, validate and plan, open the PR, then the workflow's plan and apply; no exclusion, no UI marking, no gate change | `tools/sonar-triage/sonar_triage.py` |

Planned ([epic #9](https://github.com/swarm-routing/skills/issues/9)): the ns-3-specific `ns3-new-module` (#12), `ns3-anchor-run` (#13) and `ns3-campaign` (#42); `repo-settings` (#44); `vcpkg-port` (#121).

## Install

**Any agent, with skills.sh:**

```bash
npx skills add swarm-routing/skills                       # pick skills and agents interactively
npx skills add swarm-routing/skills --skill fidelity-sheet  # one skill
```

**Claude Code, as a plugin:**

```
/plugin install swarm-routing --marketplace swarm-routing/skills
```

**Every session in an org repository**: commit this to the repository's
`.claude/settings.json` (`org-sync` writes and checks these keys):

```json
{
  "extraKnownMarketplaces": {
    "swarm-routing": { "source": { "source": "github", "repo": "swarm-routing/skills" } }
  },
  "enabledPlugins": { "swarm-routing@swarm-routing": true }
}
```

The plugin route follows `main`: Claude Code picks up new commits when it
refreshes the marketplace. The skills.sh route copies the skills at install
time; run `npx skills update` to get later commits. To review changes before
your sessions load them, pin the plugin source to a tag or commit (see
[SECURITY.md](SECURITY.md)).

**The `swarm-mcp` MCP server.** The plugin also starts
[`swarm-mcp`](https://github.com/swarm-routing/swarm-mcp), a local,
read-only stdio server whose tools (`fidelity_check`, `fidelity_row`,
`fidelity_verify`, `protocol_review`, `release_ready`, `release_after`,
`lock_verify`) run the same scripts as the skills and return their summary,
capped. It lives in its own repository, versioned and released on its own
(its `docs/adr/0002`); the plugin's `.mcp.json` runs `tools/mcp/swarm-mcp`,
which starts it at the commit [`swarm-mcp.lock`](swarm-mcp.lock) pins
(`SWARM_MCP_DIR=<checkout>` runs a local one instead). In any other MCP
client, register `python3 -I <checkout of swarm-mcp>/tools/swarm-mcp/swarm_mcp.py`
(`--list` prints the tools; `ORG_TOOLS_DIR` points it at a local
`swarm-routing/.github`).

## Add a skill

1. Create `skills/<name>/SKILL.md` in the [Agent Skills format](https://agentskills.io/specification):
   - `name` equals the directory;
   - `description` says what the skill does **and when to use it**;
   - optional `license`, `compatibility` and `metadata`;
   - under 500 lines.
2. Name the skill after its task. If it only applies to ns-3 work, prefix it with `ns3-`.
3. Anything the skill runs goes in `skills/<name>/scripts/` as a thin wrapper around a script in `swarm-routing/.github` `tools/`, which works without the skill (org rule 9). A wrapper that fetches a repository copies the `cached-checkout` block from an existing one unchanged (`check-plugins.py` checks the copies are identical).
4. Test cases go in `skills/<name>/evals/<case>/`: `prompt.md`, `case.yaml` and `graders/`. A criterion that needs judgement is a `graders/NN.md` (`type: llm`). A criterion a script can decide ("check_docs.py passes", "no stub file was created") is an executable `graders/NN.sh`:
   - its header line `# grader: <criterion>` is the expectation's text;
   - it runs as `NN.sh REPO OUTPUTS`, and exit 0 is a pass, 77 "cannot grade this run", anything else a fail.

   `tools/evals/grade.py <workspace>` runs them on every run of a skill-creator workspace and lists the `.md` graders as needing judgement; `--write` merges the results into each run's `grading.json`. `claude plugin eval` reads only the `.md` graders.
5. Bump the plugin's version in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cz.toml` and `CITATION.cff` together (rule 12).
6. Run the checks:
   - `make test` validates the manifests and every skill against the spec;
   - `claude plugin validate .` is Claude Code's own check.

## Delegate to `org-worker`

The plugin ships one subagent, [`org-worker`](agents/org-worker.md)
(`swarm-routing:org-worker`; #186). It starts with `omitClaudeMd: true`, so
it loads none of the attached repositories' CLAUDE.md and AGENTS.md files, and
reads its own repository's agent files as its first step. The contract: the
orchestrator names one repository (its checkout path) and the task; the worker
works there only and reports back. It adds no tool, server or permission
(golden rule 10); it only removes context. In a 13-repository session the
attached agent files are about 115,000 tokens (`token_audit.py files`,
estimate); the worker reads back the 6,500 to 12,000 of its own repository,
so every request it makes carries about 100,000 tokens less.

<!-- org-sync:begin develop -->
## Develop

New here? [docs/development.md](docs/development.md) is the developer guide:
the tools to install, how to get the code and its dependencies, how to
build, test, run and lint it, the Docker images, what CI checks and how to
read a red run. How changes are proposed, reviewed and released is the org's
[CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md).
Whether a regression here gets an RCAPA (root cause analysis with corrective
and preventive actions), and how: [docs/rcapa/README.md](docs/rcapa/README.md).
<!-- org-sync:end develop -->

<!-- org-sync:begin citing -->
## Releases & citing

Versions follow [SemVer](https://semver.org) ([CHANGELOG.md](CHANGELOG.md)). Each release is listed under [Releases](https://github.com/swarm-routing/skills/releases), built by the org's release workflow and archived on [Zenodo](https://zenodo.org) with its own DOI.

To cite this repository, use the “Cite this repository” button (from [CITATION.cff](CITATION.cff)). It has no DOI yet: the concept DOI appears here and in the badge above once Zenodo archives its first release.

Using it in your work? Contributions are welcome, and citing it helps just as much.
<!-- org-sync:end citing -->

## Epics

<!-- epics:begin -->
<!-- Generated by swarm-routing/.github tools/epics/epics.py from the issues labelled `epic`; edit the issues, then re-run it. -->

What is planned and in progress here: the issues labelled [`epic`](https://github.com/swarm-routing/skills/issues?q=label%3Aepic). An epic's open sub-issues carry a `priority:*` and a `model:*` label, so a contributor or an AI agent can pick one up ([how issues work](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#issues)). The whole org's plan: the [roadmap](https://github.com/swarm-routing/.github/blob/main/ROADMAP.md#epics).

| Epic | Status | Sub-issues closed |
|------|--------|-------------------|
| [#9](https://github.com/swarm-routing/skills/issues/9) Protocol-development and org-ops skills: fidelity sheets, invariant review, module scaffolds, anchors, handoffs | In progress | 3 / 13 |

<details><summary>Closed: 1 epic</summary>

| Epic | Closed |
|------|--------|
| [#129](https://github.com/swarm-routing/skills/issues/129) developer experience: a newcomer can build, test and contribute from the docs alone | Done 2026-11-16 |

</details>

<!-- epics:end -->

## Licence

See [LICENSING.md](LICENSING.md).
