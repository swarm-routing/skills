# ARA

<!-- org-sync:begin badges -->
[![Licence](https://img.shields.io/badge/licence-GPL--2.0--only-blue)](LICENSING.md)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow)](https://www.conventionalcommits.org)
<!-- org-sync:end badges -->
[![Core coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fswarm-routing.github.io%2FARA%2Fbadges%2Fcoverage.json)](https://github.com/swarm-routing/ARA/actions/workflows/core.yml)

ARA is the Ant-Colony-Based Routing Algorithm of Güneş, Sorges & Bouazizi (2002),
written here as a simulator-agnostic `core/` and an ns-3 module on swarm-core;
it replaces AntHocNet's `ara` comparator arm. The core is in progress and the
ns-3 module is planned. Its page on the site is
[swarm-routing.github.io/projects/ARA](https://swarm-routing.github.io/projects/ARA/),
and it builds in the `ghcr.io/swarm-routing/ns3-dev` image.

## Quick start

```bash
make test
```

## Layout

```
core/       the algorithm
ns3/        (planned) the ns-3 module
```

## Epics

<!-- epics:begin -->
_No epics yet._
<!-- epics:end -->

## Working here

Read [AGENTS.md](AGENTS.md) before changing anything.

## License

Per directory: see [LICENSING.md](LICENSING.md).
