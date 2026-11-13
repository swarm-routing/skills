# CONTEXT.md — orientation and history

Background an agent or a new contributor needs that does not belong in
`AGENTS.md`: domain notes, current state, glossary, open questions. Read the
section a task needs, not the whole file.

## Current state

One tree, published two ways (golden rule 13): as the Claude Code plugin
**`swarm-routing`** (marketplace `swarm-routing`; any org repository enables
it from its committed `.claude/settings.json`, swarm-routing/.github#10; the
plugin was called `org-repo` until 2026-11-09, and `marketplace.json` records
the rename), and as plain Agent Skills that skills.sh installs into any agent
(`npx skills add swarm-routing/skills`).

Eight skills under `skills/`: `org-repo`, `fidelity-sheet`, `protocol-review`,
`docs-review`, `pr-shepherd`, `lit-search`, `references` and `token-audit`
(what each does: the README table). Each is a procedure over a script in
swarm-routing/.github `tools/`, reached through a thin wrapper in
`skills/<name>/scripts/`; `token-audit`'s script is this repository's own
`tools/token-audit/token_audit.py`.

How a skill is tested: its eval cases in `skills/<name>/evals/<case>/` are run
with and without the skill (skill-creator, or `claude plugin eval`), then
graded: `tools/evals/grade.py` runs the script graders and a model judges the
rest. `make test` checks the manifests, every skill against the Agent Skills
spec, every grader's shape, and the wrappers' cached-checkout block
(`tools/checks/check-plugins.py`, `test_wrapper_cache.py`). `org-repo` has no
eval cases yet (#102).

Next work: epic #9 and its open sub-issues. Skills still to write:
`ns3-new-module` (#12), `ns3-anchor-run` (#13), `ns3-campaign` (#42),
`release` (#43), `repo-settings` (#44). Releases of this repository: #64.
Work in flight is in the newest open `handoff` issue.

## Glossary

- **Skill**: a directory `skills/<name>/` whose `SKILL.md` is a procedure an
  agent follows (the Agent Skills spec). It orders a script's commands and
  says where judgement is needed; it holds no logic of its own (golden rule
  11).
- **Wrapper**: a script in `skills/<name>/scripts/` that finds and runs one
  tool of swarm-routing/.github (or of this repository) and does nothing
  else.
- **Cached checkout**: the block every fetching wrapper carries unchanged. It
  keeps one immutable snapshot of a repository per ref and commit under the
  user's cache directory, updated under a lock, so a tool's files never
  change while it runs. `ORG_TOOLS_DIR` (and `ORG_SYNC_DIR` for org-sync)
  points a wrapper at a local checkout instead.
- **Eval case**: `skills/<name>/evals/<case>/`: a `prompt.md` (the task given
  to an agent), a `case.yaml` (the expected outcome, and the script that
  builds the fixture) and `graders/`.
- **Grader**: one criterion of an eval case. `graders/NN.md` (`type: llm`) is
  judged by a model; `graders/NN.sh` is a script (`NN.sh REPO OUTPUTS`: exit
  0 pass, 77 cannot grade, anything else fail) run by `tools/evals/grade.py`.
