# AGENTS.md (fixture: swarm-routing/ns3-tools)

Python readers under `python/ns3_tool/`, stdlib only, tests in `python/tests/`.

## Build & verify

```bash
python3 -m unittest discover -s python/tests -t .
```

Golden rules: 5. Determinism (no unordered iteration reaching an output). 13. Statistics stay scripted.
A bug fix comes with a reproducing test first.
