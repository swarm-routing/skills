---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Both are reviewed: merge ns3-swarm-core#20 and ARA#12 (ARA builds against swarm-core's main, so the order matters). Also draft the comment for ARA#12 telling people that issue #5 stays open until the anchor run is done; put it in actions.md.

This sandbox cannot reach the GitHub API (cloning a repository still works). `export PATH=$PWD/.fake-gh:$PATH` gives you a `gh` that serves the recorded API for these PRs (read-only). It refuses every write, so `pr-status merge` can only run with `--dry-run` here. The GitHub MCP tools aren't here either: write each reply you would post, each thread you would resolve and each merge you would make, in order, to `actions.md` instead, and don't push. The recorded CI never changes, so a `wait` won't see it move: give it a short --timeout.
