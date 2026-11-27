---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

You're the coordinator for the swarm-routing org. Continue from the handoff issue: run the next pass over its tickets.

This sandbox cannot reach GitHub or start sessions. `handoff.md` is the handoff issue as it reads now, `status.txt` is what `status.py` printed a minute ago, and `tickets/` holds each ticket's body. Don't try to fetch them again. Instead of acting, write each action you would take (a session you would start, with its title, tags and the one repository attached; a check-in you would schedule; a comment or issue you would post, with its text), in order, to `actions.md`, and each worker's brief, in full, to `briefs/<repository>.md`. Don't commit.
