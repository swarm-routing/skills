# Security Policy

`swarm-routing/skills` is the org's agent tooling: Claude Code skills (instructions) and thin wrappers, no simulation code. This document records its
security posture honestly; it promises nothing the code does not do. The
org-wide policy is [swarm-routing/.github SECURITY.md](https://github.com/swarm-routing/.github/blob/main/SECURITY.md).

## Trust boundary

The skill text and any command a skill tells the agent to run. A skill is
instructions that an agent follows with the permissions of the session that
loads it, in every repository that enables this marketplace, so a change
merged here reaches every org repository's agent sessions. Skills hold
procedures only: every action they take is a script in
`swarm-routing/.github` `tools/` (org rule 9), which works without the
skill. Every change is reviewed in a pull request before it reaches `main`,
which is what sessions load.

## Known, by-design limitations (out of scope)

- **A skill cannot restrict what an agent may do.** The session's permission
  mode and the person approving tool calls decide that; a skill only says what
  to do.
- **The marketplace follows `main`.** A repository that enables it gets every
  merged change on its next session. To review changes first, pin the
  marketplace to a tag or commit in `.claude/settings.json`.

## What to report privately

- A skill that instructs an agent to send data anywhere, to weaken or skip a
  check, to change permissions or repository settings, or to run something
  other than what its text says it runs.
- A wrapper script under `plugins/*/skills/*/scripts/` that does more than
  locate and call the org tool it names.
- A compromised or tampered `.claude-plugin/marketplace.json` or
  `plugin.json` (for example a `source` that points outside this repository).

<!-- org-sync:begin reporting -->
## Reporting a vulnerability

Report privately through GitHub's private vulnerability reporting: the
repository's **Security** tab, then **Report a vulnerability**. If that is
not available, open an issue that only asks for a private contact, and put
no vulnerability details in it. This is a research project maintained on a
best-effort basis: expect an acknowledgement within a few days, not an SLA.
<!-- org-sync:end reporting -->

## Verifying what it ships

There is nothing to download. To pin what your sessions load, set the
marketplace source in `.claude/settings.json` to a reviewed tag or commit
instead of `main`, and compare `git log` of this repository before moving it.
