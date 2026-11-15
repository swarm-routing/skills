---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

This is swarm-routing/demo. Everything for 0.5.0 is merged. I'm the maintainer: please cut the v0.5.0 release now.

This sandbox cannot reach the GitHub API, but git and HTTPS downloads from github.com work. `export PATH=$PWD/.fake-gh:$PATH` gives you a `gh` that serves the recorded API for this repository (read-only); it refuses every write and every command but `gh api`. The GitHub MCP tools aren't here either: write each action you would take on GitHub (a workflow dispatch, a PR you would open, a merge), in order, to `actions.md` instead, with its content, and don't push.
