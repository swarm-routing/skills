---
name: protocol-review
description: "Review a swarm-routing protocol or tool change against the org's golden rules before a pull request or during review: licence headers per directory, the core/ include boundary, versioned wire formats, no module named core, determinism, paired comparisons, bounded structures, pinned CI, nothing shipped depending on .claude/, plus the repository's own rules. Use whenever a diff touches core/, ns3/, model/, a wire format, a CMakeLists, a workflow or a benchmark claim in any org repository (ARA, BeeAdHoc, Termite, HOPNET, ns3-swarm-core, ns3-tools), when asked to review a PR there, or before pushing one. Script first: check_invariants.py does the mechanical rules; you judge the rest."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/check-invariants clones swarm-routing/.github tools/protocol-review).
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# protocol-review

Every org repository carries the same nine golden rules (AGENTS.md, rules 1–9)
plus its own (10 onwards). The cheap ones are checked by a script; the ones
that need judgement are yours. Run the script first, so your attention goes
to what it cannot see.

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/protocol-review"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
"$SKILL"/scripts/check-invariants . --base origin/main   # in the repo under review
"$SKILL"/scripts/check-invariants . --base origin/main --pr-body PR.md   # once the PR text exists, saved as PR.md
```

`--pr-body` takes a file that exists (the script stops otherwise): leave it
out until the PR text is written.

Inside a `swarm-routing/.github` checkout, `python3 -I
tools/protocol-review/check_invariants.py <repo>` is the same;
`ORG_TOOLS_DIR=<checkout>` points the wrapper at a local one.

## 1. Run the mechanical checks

The script prints one line per rule it could check, `PASS`, `WARN` or
`FAIL`, with the files or lines under it, and exits 1 only on a FAIL:

| Rule | Checked | Level |
|---|---|---|
| 1 licensing | each changed source file's SPDX against its directory (`dual` in `.github/org-sync.toml`); a new top-level directory without a `LICENSING.md` row | FAIL; WARN |
| 2 licence boundary | `core/` includes only the standard library and `core/` headers | FAIL |
| 3 wire formats | a wire file changed without the version constant in the diff | WARN |
| 4 module name | a contrib module named `core` | FAIL |
| 5 determinism | libc `rand`, `time(nullptr)` or a wall clock (FAIL in `core/`, WARN elsewhere); an unordered container in `core/` (WARN) | FAIL / WARN |
| 8 CI hygiene | an action not pinned by full SHA with `# vX.Y.Z`; `retention-days` over 7 | FAIL |
| 9 `.claude/` | a shipped file calling a `.claude/` script | FAIL |
| tests | `core/` logic changed, no core test changed | WARN |
| 6 comparisons | a changed Markdown line or the `--pr-body` text claiming a comparison with fewer than 20 seeds, or none | HINT |
| 7 bounded | a container added under `core/` or a simulator directory that grows in the diff with nothing bounding it in sight | HINT |

A repository sets its paths in a `[review]` table of `.github/org-sync.toml`
(`core`, `core_tests`, `wire`, `wire_version`, `sim_dirs`). If the wire rule
says `set review.wire_version`, the repo has a wire format and no config yet:
say so in the review rather than guessing the file names.

**A FAIL is fixed in the code, never by weakening the script or the config.**
A WARN is confirmed or explained in the PR body, one line each.

## 2. Judge what the script cannot

Start from the HINT lines: each names a file and line where rule 6 or 7 may
be broken. A HINT never fails the run and is not a finding by itself. Judge
every item under it, not the group: confirm each (a blocking finding) or
dismiss it with a reason in one line. The text output lists 12 items per rule
and ends with `… and N more` when there are others; then run again with
`--json`, which lists them all. Then read the
rest of the diff for these; each needs a sentence in the review, even when the
answer is "not touched":

- **Rule 3, the rest of it.** A new or changed control header is a POD with a
  leading version byte, little-endian bounds-checked readers and writers, and a
  roundtrip *and* a fuzz test in the same PR. A changed field or unit bumps the
  version even if the size is the same.
- **Rule 5, the rest of it.** Randomness reaches `core/` only through the
  injected RNG port, time through the clock port. Ordering that reaches an
  output (a trace, a marker line, a decision) never depends on an unordered
  container or a pointer value.
- **Rule 6, comparisons.** Any number in the PR (body, docs, a commit
  message) that compares protocols comes from per-seed paired deltas over at
  least 20 seeds, from the canonical marker lines, with the run linked. A
  comparator arm's number counts only after its three gates (fidelity sheet,
  delivery smoke, anchor). Five seeds, unpaired means or a claim without a run
  is a blocking finding.
- **Rule 7, bounded structures.** Every new container that grows with traffic
  (histories, visited paths, dedup sets, queues, pheromone tables) has a
  configured cap, and the cap has a test or a Parameters row. `push_back` in a
  receive path with no eviction is the usual miss.
- **Rule 2, the other direction.** A dual-licensed script imports no GPL-only
  code; code taken from AntHocNet keeps its licence and records its
  provenance; nothing is copied from ns-3's `src/aodv` or `src/olsr`.
- **Sources.** A source added to or dropped from `docs/fidelity.md` as the
  one the protocol implements is also added to or dropped from
  `[[references]]` in `.github/org-sync.toml` (its DOI confirmed with
  `lit_search.py confirm`, or a URL and the reason it has none), with
  `org_sync.py apply` and the CITATION.cff update (a reseed, unless
  `org_sync.py seeds` shows hand-added fields; then by hand) in the same PR.
  The `docs-review` script checks that each configured work reached
  CITATION.cff with a DOI or its reason; whether the list matches the
  sources `docs/fidelity.md` relies on is yours to judge.
- **The repository's own rules (10 onwards).** Read them in its AGENTS.md:
  protocol repos require the fidelity sheet before `core/`, pre-registered
  interpretations, written-fresh `core/` code; ns3-tools requires
  non-intrusive probes and append-only marker lines.

## 3. Report

One short block, in the PR body or as the review:

```
check_invariants: <last line, e.g. "WARN  review the warnings above">
- rule 3: <WARN explained, or "wire header v2 → v3, roundtrip + fuzz in test/">
- rule 6: <the claim, its seeds and run, or "no comparison claimed">
- rule 7: <each new growing container and its cap, or "none added">
- repo rules: <which ones applied and how they hold>
blocking: <each finding that must be fixed, or "none">
```

Name a finding by file and line. Do not approve or merge: the review states
findings; the maintainer decides.
