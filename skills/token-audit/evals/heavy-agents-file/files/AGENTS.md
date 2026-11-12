# AGENTS.md

Guide for AI coding agents working in `antlab`. Read this before changing anything.

## What this repo is

**Status (2026-10-28): the core and the adapter are merged (#12, #19). The trail table was rewritten on 2026-10-30 (#31) and the scenario generator landed on 2026-11-02 (#40); the release workflow is planned (#44) and the plotting tool is in progress (#47).**

`antlab` is a small ant-routing protocol used to try mechanisms before they go to a real protocol: a simulator-free `core/` and a thin `adapter/`.

```
core/      the algorithm and its unit tests (no simulator headers)
adapter/   the simulator adapter: converts headers, carries out decisions, owns timers
tools/     standalone scripts (see Tools)
docs/      wire.md (the header layouts), README.md (the docs map)
```

## Build & verify

```bash
make test     # core unit tests, no simulator
make check    # everything CI gates on: format, headers, tests
```

Always run `make test` before committing a core change.

## Golden rules (invariants, do not break)

Org-wide (1-3), then this repo's own.

<!-- org-sync:begin org-rules -->
1. **Licensing per directory.** Every original source file starts with the copyright line and its
   SPDX identifier, matching its directory in `LICENSING.md`; a new directory gets its row there in
   the same PR.
2. **Determinism.** A fixed `--seed=<N>` gives byte-identical output. All randomness goes through
   the seeded stream; never libc `rand()`, wall-clock time or unordered-container iteration order
   in anything that reaches an output.
3. **CI hygiene.** Actions are pinned by full commit SHA with a version comment, every job that
   runs steps has a `timeout-minutes` cap, and transient artifacts keep `retention-days` at 7 or
   less.
<!-- org-sync:end org-rules -->
4. **`core/` never includes a simulator header.** Time, randomness and neighbours come through
   the injected ports; only `adapter/` may include simulator headers.
5. **Every trail-table change carries a core unit test** in `core/test/`, written before the fix.
6. **The trace format is append-only.** A new field goes at the end of a line; removing or
   renaming one bumps `kTraceVersion` and updates `tools/trailmix.py` in the same PR.
7. **Bounded tables stay bounded.** The trail table and the duplicate history carry the caps in
   `core/config.h`; no code path grows them past it.
8. **Papers stay out of this repository.** Cite by DOI link; copies live in the private library.

## Tools

Every script under `tools/`, what it does and when to reach for it.

- **`tools/trailmix.py`**: reads a run's trace lines and prints one row per flow: delivered, lost, mean hops; `--json`, `--self-test`. Use it before reading a trace by eye. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/antcount.py`**: counts control packets by kind from a trace and prints the overhead ratio per second. Use it when a change may add control traffic. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/seedpair.py`**: runs the same scenario on two builds for the same seeds and prints the paired difference with its interval. Use it for any before/after claim. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/scene_gen.py`**: writes a scenario's movement and flow files from a seed; `check` verifies a committed scenario still equals the generator's output. Use it when adding or changing a scenario. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/tablefuzz.py`**: feeds random insert, decay and lookup sequences to the trail table under ASan and checks its invariants. Use it after touching `core/trail-table.*`. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/wirecheck.py`**: round-trips every header through the codec and compares it with the layout table in `docs/wire.md`. Use it after touching a header. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/capwatch.py`**: reports the high-water mark of every bounded table in a run against its cap. Use it when a rule-7 question comes up. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/fmt-all.sh`**: runs the formatter over `core/` and `adapter/` and fails on a diff. Use it before every push. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/headers.sh`**: checks the licence header of every source file against `LICENSING.md`. Use it before every push. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/relnotes.py`**: builds the release notes from the merged PR titles since the last tag. Use it only when cutting a release. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/dist.sh`**: builds the release tarball and verifies it in a clean tree. Use it only when cutting a release. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/ci-times.py`**: prints each CI job's duration over the last twenty runs against its timeout. Use it when a job starts timing out. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/bisect-run.sh`**: wraps a failing seed so `git bisect run` can use it. Use it when a seed regresses. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.
- **`tools/plot-flows.py`**: draws delivery over time per flow from a trace; needs matplotlib. Use it for a report or a paper figure. It is standalone, reads only the files it is given
  and exits non-zero on its first failed check; its usage is in its docstring.

## History

The project began as a single file that mixed the algorithm with the simulator's packet classes. The first rewrite split the algorithm out so that it could be unit-tested, and found three bugs on the way: a trail that was never decayed when its neighbour disappeared, a duplicate history that grew without bound, and a tie-break that depended on container order and so changed between compilers. Each of them became a rule above. The second rewrite replaced the per-destination map with a flat table after a profile showed that lookups dominated a large run; the public interface did not change. The adapter was rewritten once, when the simulator changed the signature of its route-input hook; since then every such difference is handled by one version macro in the adapter's header, and nothing in `core/` knows the simulator's version. The trace format has been versioned since the day a renamed field silently broke the flow reader for two weeks.

## Where to look

| You want to | Go to |
|---|---|
| Change the algorithm | `core/` |
| Change how packets are carried | `adapter/` |
| The header layouts | `docs/wire.md` |
| The docs map | `docs/README.md` |
