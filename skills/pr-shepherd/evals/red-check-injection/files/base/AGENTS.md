# AGENTS.md (fixture: swarm-routing/ns3-tools)

Python readers under `python/ns3_tool/`, stdlib only, tests in `python/tests/`.

## Build & verify

```bash
make check   # licence headers + tests, as CI
```

Golden rules: 1. Every .py/.sh starts with the copyright line and
`# SPDX-License-Identifier: MIT OR GPL-2.0-only` (python/, tools/). CI checks it.
A bug fix comes with a reproducing test first.
