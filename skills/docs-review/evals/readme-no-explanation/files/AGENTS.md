# AGENTS.md — guide for AI coding agents

Operational guide for LLM agents working in `swarm-routing/ARA`.

## What this repo is

**Status: core/ in progress; ns3/ planned (#4).****

ARA, the Ant-Colony-Based Routing Algorithm (Güneş, Sorges & Bouazizi, 2002), as a standalone hexagonal protocol: a simulator-agnostic `core/` and an ns-3 `ns3/` adapter (contrib module `ara`) linking against `swarm-core`. It replaces AntHocNet's `ara` comparator arm. No benchmark has run yet: the anchor waits for the ns-3 module.

```
core/       simulator-agnostic algorithm + unit tests (MIT OR GPL-2.0-only)
ns3/        (planned, #4) contrib module `ara` (GPL-2.0-only)
```

## Build & verify

```bash
make test   # core/ unit tests
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
