# AGENTS.md — guide for AI coding agents

Operational guide for LLM agents working in `swarm-routing/Termite`.

## What this repo is

**Status: empty.** Populated in Phase 5; docs/ holds the fidelity sheet. Explain the anchor miss before code (#3).

Termite (Roth & Wicker) as a standalone hexagonal protocol: routing by stigmergy, a simulator-agnostic `core/` and an ns-3 `ns3/` adapter (contrib module `termite`) on `swarm-core`.

```
core/       simulator-agnostic algorithm + unit tests (MIT OR GPL-2.0-only)
ns3/        contrib module `termite` (GPL-2.0-only)
docs/       fidelity sheet
```

## Build & verify

```bash
make check   # everything CI gates on
```

## Golden rules (invariants — do not break)

<!-- org-sync:begin org-rules -->
Org-wide rules 1-9: see swarm-routing/.github CONTRIBUTING.md.
<!-- org-sync:end org-rules -->

## Conventions

<!-- org-sync:begin conventions -->
Issues follow the org taxonomy.
<!-- org-sync:end conventions -->

## Git workflow

<!-- org-sync:begin git-workflow -->
Branch from main; every change is a squash-merged PR.
<!-- org-sync:end git-workflow -->

## Agent skills

<!-- org-sync:begin skills -->
The org's skills ship as the `swarm-routing` plugin.
<!-- org-sync:end skills -->

## Where to look

| You want to… | Go to |
|---|---|
| The org's invariants | swarm-routing/.github CONTRIBUTING.md |
