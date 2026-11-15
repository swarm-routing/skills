---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

ARA needs swarm-core's new `PheromoneTable::decayAll`, which is only on swarm-core main so far, so I changed core/CMakeLists.txt to fetch swarm-core main and dropped to C++20 so older toolchains build it. It's uncommitted in this repo's working tree. Review it before I push: what blocks it, and what should I do instead?
