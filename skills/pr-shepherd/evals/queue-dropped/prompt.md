---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

ns3-tools#57 was reviewed and I asked for it to be merged yesterday: auto-merge was enabled and it was green. It still is not on main. Find out where it stands and get it merged, or tell me exactly what it needs.

This sandbox cannot reach the GitHub API (cloning a repository still works). `export PATH=$PWD/.fake-gh:$PATH` gives you a `gh` that serves the recorded API for this PR (read-only). It refuses every write. The GitHub MCP tools aren't here either: write each action you would take on GitHub (a reply, enabling auto-merge, a merge, a branch update), in order, to `actions.md` instead, and don't push. The recorded state never changes, so a wait won't see it move: give it a short --timeout. The logs of workflow runs are not recorded.
