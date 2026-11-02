# AGENTS.md — guide for AI coding agents

Operational guide for LLM agents working in `swarm-routing/skills`. Read this
before changing anything. Org-wide conventions:
[`swarm-routing/.github` CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md). Shape and rules mirror
[AntHocNet's AGENTS.md](https://github.com/danieljoppi/AntHocNet/blob/main/AGENTS.md), the source repository.

## What this repo is

The swarm-routing **Claude Code plugin marketplace**: org-wide skills that any
org repository enables from its committed `.claude/settings.json`
(swarm-routing/.github#10). The first plugin is `org-repo`: set up or update a
repository from the org templates (badges, README, AI files, ADRs, licence,
security policy, Makefile targets) through `tools/org-sync`, script first.

```
.claude-plugin/marketplace.json            the marketplace: one entry per plugin (name, ./source, version)
plugins/<plugin>/.claude-plugin/plugin.json the plugin manifest (version equals the marketplace entry)
plugins/<plugin>/skills/<skill>/SKILL.md   the procedure; frontmatter name = directory, description <= 1024 chars
plugins/<plugin>/skills/<skill>/scripts/   thin wrappers only (org rule 9)
tools/checks/check-plugins.py              validates all of the above (+ test_check_plugins.py)
.github/org-sync.toml                      this repo's org-sync config (kind = "skills")
```

## Build & verify

```bash
make help    # the org's standard target names: build, test, lint, format, check, clean, shell, ci
make test    # check-plugins.py + its self-test
make check   # what CI gates on: lint, test, licence headers, org-sync check
ORG_SYNC_DIR=/path/to/swarm-routing/.github plugins/org-repo/skills/org-repo/scripts/org-sync plan .
```

## Golden rules (invariants — do not break)

Org-wide (1–9), then this repo's own.

<!-- org-sync:begin org-rules -->
1. **Licensing per directory, as AntHocNet** ([`LICENSING.md`](LICENSING.md);
   AntHocNet [LICENSING.md](https://github.com/danieljoppi/AntHocNet/blob/main/LICENSING.md),
   [ADR-0028](https://github.com/danieljoppi/AntHocNet/blob/main/docs/adr/0028-core-is-dual-licensed.md)). A
   simulator-free `core/` and the standalone tooling are `MIT OR GPL-2.0-only`;
   ns-3 modules, the site, docs and data are `GPL-2.0-only`. Every original
   `.h`/`.hpp`/`.cc`/`.cpp`/`.py`/`.sh` starts with
   `// Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)` +
   `// SPDX-License-Identifier: <MIT OR GPL-2.0-only | GPL-2.0-only>` (`#`
   comments where needed), matching its directory in `LICENSING.md`. CI
   (`reusable-licence-check.yml`) checks it. A new directory gets its row in
   `LICENSING.md` in the same PR.
2. **The licence boundary only goes one way.** GPL code may use the dual
   parts; dual code never pulls GPL-only code in: a `core/` file includes only
   the C++ standard library and other `core/` files (CI checks it), and a dual
   script imports no GPL-only code. Code coming from AntHocNet keeps its
   licence: its `core/`/`tools/` (dual) may land in dual or GPL paths here; its
   `ns3/` modules and `web/` (GPL-2.0-only) only in GPL paths. Third-party code
   (AntHocNet's vendored `aomdv`/`gpsr`, IITP RAS) lands only in GPL paths with
   its provenance recorded. Write clean implementations against public ns-3
   interfaces rather than copying ns-3's `src/aodv`/`src/olsr`.
3. **Wire formats are POD + versioned.** Control headers are
   simulator-independent POD structs with bounds-checked little-endian
   readers/writers, a leading version byte, and deterministic roundtrip + fuzz
   tests. Changing a field or its units bumps the version byte.
4. **No contrib module named `core`** (collides with ns-3's `src/core`). The
   shared module is `swarm-core` (`#include "ns3/swarm-core-module.h"`).
5. **Determinism.** A fixed `--seed=<N>` gives byte-identical output. All
   randomness through the simulator's seeded streams or an injected RNG port;
   never libc `rand()`, wall-clock time, or unordered-container iteration order
   in anything that reaches an output.
6. **Comparisons are paired.** Per-seed deltas across >= 20 seeds, emitting the
   canonical `##CONFIG##`, `##RUN##`, `##BENCH##`, `##DIAG##` lines. A
   comparator arm (a protocol we did not design) counts only after its three
   gates: a fidelity sheet from its paper, the per-PR delivery smoke, and an
   anchor reproducing the paper's own trend.
7. **Keep bounded structures bounded** (visited paths, dedup histories, queues
   carry a configured cap).
8. **CI hygiene.** Actions pinned by full commit SHA with a `# vX.Y.Z` comment;
   buildx caches scoped per profile; transient artifacts `retention-days` <= 7.
9. **Nothing shipped depends on `.claude/`.** Skills hold procedures; scripts
   that anything shipped needs live in `tools/` (AntHocNet ADR-0014).
<!-- org-sync:end org-rules -->
10. **This repo is a trust boundary** ([SECURITY.md](SECURITY.md)). A merged skill
    runs with the permissions of every session in every repo that enables the
    marketplace. Every change is a reviewed PR; no skill tells an agent to
    weaken a check, change permissions or settings, or send data anywhere.
11. **Skills are procedures; scripts do the work** (AntHocNet ADR-0014). A
    skill's steps are commands of a script in `swarm-routing/.github` `tools/`
    (or this repo's `tools/`) that works without the skill, and the agent reads
    the script's summary, not raw files.
12. **Versions move together.** A plugin change bumps its `plugin.json`
    version and its marketplace entry in the same PR (`check-plugins.py`).

## Conventions

<!-- org-sync:begin conventions -->
- Issues follow the org taxonomy ([CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#issues), from
  [AntHocNet ADR-0013](https://github.com/danieljoppi/AntHocNet/blob/main/docs/adr/0013-track-bugs-and-findings-as-issues.md)): one type label
  (`bug`/`enhancement`/`chore`/`documentation`/`verification`, plus `epic` for
  umbrellas), area label(s) (`protocol`/`adapter`/`ns3`/`benchmark`/
  `observability`/`packaging`/`learn-site`/`literature`), one `model:*`
  recommendation, one `priority:P1|P2|P3` on non-epic issues, a
  `release:vX.Y.Z` label only when a roadmap gates the issue. Labels come from
  `labels.json` via the `sync-labels` workflow.
- Issue bodies: **Context** (evidence, numbers, links) · **Scope** ·
  **Acceptance criteria** (checkboxes) · **Depends on** (cross-repo form
  `swarm-routing/<repo>#N`) · **References**. Children of an epic say "Part of
  #N" and are linked as sub-issues. Comments you post end with the Claude Code
  footer.
- Issues migrated from AntHocNet carry `migrated` and start with *Migrated from
  `danieljoppi/AntHocNet#N`*.
- Make minimal, reviewable changes; update the relevant doc/ADR when you change
  a documented decision.
<!-- org-sync:end conventions -->

## Git workflow

<!-- org-sync:begin git-workflow -->
- Branch from `main` (`claude/<short-topic>`), one focused change per PR.
- **Always open a PR to `main`** once the branch is pushed — every change is
  tracked through one.
- **PRs are squash-merged** (the only merge method enabled). The PR title is
  the commit on `main`, so it is a lowercase Conventional Commit
  (`feat:`/`fix:`/`docs:`/`chore:`/`ci:`…, optional scope).
- Push with `git push -u origin <branch>`; merge when CI is green.
<!-- org-sync:end git-workflow -->

## Where to look

| You want to… | Go to |
|--------------|-------|
| The org's invariants, labels, issue shape | [`swarm-routing/.github` CONTRIBUTING.md](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md) |
| How Claude Code plugins and marketplaces work | Claude Code docs: plugins, plugin marketplaces, skills |
| The org templates the `org-repo` skill applies | `swarm-routing/.github` `templates/`, `tools/org-sync/` |
| The script-first model | AntHocNet ADR-0014, its `.claude/skills/benchmark-results` |
| Record an architecture decision | [`docs/adr/`](docs/adr/) (`0000-template.md`) |
| Pick up open work | this repo's issues — highest open `priority:P*` first; newest open `handoff` issue for work in flight |
