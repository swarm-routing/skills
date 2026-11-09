# Termite

<!-- org-sync:begin badges -->
[![Licence](https://img.shields.io/badge/licence-GPL--2.0--only-blue)](LICENSING.md)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow)](https://www.conventionalcommits.org)
[![Colony Arena](https://img.shields.io/badge/Colony%20Arena-Termite-8a5a2b)](https://swarm-routing.github.io/arena/Termite/)
[![ns3-dev image](https://img.shields.io/badge/image-ns3--dev-2496ED?logo=docker)](https://github.com/orgs/swarm-routing/packages/container/package/ns3-dev)
<!-- org-sync:end badges -->

**Status: alpha.** Termite (Roth & Wicker, 2003) is routing by stigmergy: the routing state rides inside data packets and there are no control ants. This repository will hold it as a standalone core/ and ns-3 module; the [fidelity sheet](docs/fidelity.md) comes first.

## Quick start

```bash
docker run --rm -v "$PWD:/src/termite:ro" ghcr.io/swarm-routing/ns3-dev:latest-debug ns3-build-contrib --test termite=/src/termite/ns3
./ns3 run termite-example
```

## Epics

<!-- epics:begin -->
_No epics yet._
<!-- epics:end -->

## Working here

Read [AGENTS.md](AGENTS.md) before changing anything.

## License

Per directory: see [LICENSING.md](LICENSING.md).
