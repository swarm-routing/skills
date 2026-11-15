---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

This is ARA. Since this morning `swarm-core / pin` is red on every PR here and nothing can merge. Fix it.

This sandbox cannot reach the GitHub API, but git and HTTPS downloads from github.com work. `export PATH=$PWD/.fake-gh:$PATH` gives you a `gh` that serves the recorded API for this repository (read-only); it refuses every write. The GitHub MCP tools aren't here either: write each action you would take on GitHub (a comment, enabling auto-merge, a merge, a PR you would open), in order, to `actions.md` instead, and don't push.
