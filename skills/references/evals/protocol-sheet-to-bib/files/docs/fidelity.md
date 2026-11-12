# ARA fidelity sheet

| Mechanism | Source | Implementation |
|---|---|---|
| Forward and backward ants create trails | [G02] §3.1 | `core/ara-router.cc` |
| Data packets reinforce the trail | [G02] §3.2, restated in [R05] §3.5.2 | `core/ara-router.cc` |
| Duplicate error handling | [GKB03] §2 | planned |

## Sources

<!-- fidelity:sources:begin -->
| Key | Citation | Access |
|---|---|---|
| G02 | M. Güneş, U. Sorges, I. Bouazizi, *ARA – The Ant-Colony Based Routing Algorithm for MANETs*, ICPP Workshops 2002, pp. 79–85 | in the library |
| R05 | M. H. Roth, *Termite: A Swarm Intelligent Routing Algorithm for Mobile Wireless Ad-Hoc Networks*, PhD dissertation, Cornell University, 2005 | in hand |
| GKB03 | M. Güneş, M. Kähmer, I. Bouazizi, *Ant-Routing-Algorithm (ARA) for Mobile Multi-Hop Ad-Hoc Networks – New Features and Results*, Med-Hoc-Net 2003 | listed in MANUAL-DOWNLOADS.md |
<!-- fidelity:sources:end -->

Also read: a 2012 comparison paper (in the library) that restates [G02] §3.
