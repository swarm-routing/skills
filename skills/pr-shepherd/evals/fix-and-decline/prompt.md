---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Please shepherd ns3-tools#41 (its branch is checked out here): deal with the open review threads.

This sandbox cannot reach the GitHub API (cloning a repository still works). `export PATH=$PWD/.fake-gh:$PATH` gives you a `gh` that serves the recorded API for these PRs (read-only). The GitHub MCP tools aren't here either: write each reply you would post, each thread you would resolve and each merge you would make, in order, to `actions.md` instead, and don't push.
