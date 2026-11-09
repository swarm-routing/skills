# AGENTS.md — guide for AI coding agents

Operational guide for LLM agents working in `swarm-routing/ns3-tools`.

## What this repo is

**Status: being populated (Phase 4).****

Protocol-agnostic diagnostics and comparison tooling.

```
ns3/        the routing-bench module (GPL-2.0-only)
python/     the readers (MIT OR GPL-2.0-only)
docs/       marker-line contract, arena reference
```

## Build & verify

```bash
for t in python/tests/test_*.py; do python3 "$t"; done
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
