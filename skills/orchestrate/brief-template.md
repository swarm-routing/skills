# Worker brief template

The coordinator fills the `<...>` fields and sends the result as the
worker's first message. Keep every line: each one is there because a pass
without it cost a worker (swarm-routing/.github#1005, "Brief"). Add the
ticket's own specifics under **Task**; never remove a rule.

## Isolation checklist (run before sending)

- [ ] The scope line names **one** repository, and it is the only one the
      worker's session attaches. A read-only look at another repository is
      named in the brief as read-only, with what to read.
- [ ] No other worker is running in that repository (the pass table).
- [ ] **AntHocNet** work goes only to its own isolated worker: a session
      started for AntHocNet alone, tagged `gpl-protocol-worker`, whose brief
      names no MIT or dual-licensed (`MIT OR GPL-2.0-only`) repository, path
      or file (no swarm-core, no protocol `core/`, no `tools/` of another
      repository) and asks for nothing to be carried out of AntHocNet. A
      release it consumes is given as the values to pin (tag, commit), never
      as a repository to open, read or change. Its
      GPL-only code (`ns3/`, `web/`, the vendored `aomdv`/`gpsr`) lands only
      in GPL paths (golden rules 1 and 2). A task that also needs a change in
      a dual-licensed repository is two workers: that one first, by its own
      brief, then AntHocNet's with the merged commit.
- [ ] A cross-repository dependency is named by its merged commit, read from
      the PR (`.merge_commit_sha`), never "the latest main".
- [ ] Nothing in the brief comes from a worker's or another session's report
      without having been verified (SKILL.md step 5), and no scope, gate or
      policy change is asked without the maintainer's own words.

## The brief

```markdown
Scope: ONLY swarm-routing/<repo>. Ticket: swarm-routing/<repo>#<N> (<title>).
<If any:> Read-only: swarm-routing/<other> <path>, to <why>.

Read <repo>'s AGENTS.md (and what CLAUDE.md imports) first; read no other
repository's agent files.

Task: <what done means, in the ticket's own acceptance criteria; the order of
the steps; the merged commit of any dependency>.

How:
1. Ticket first: work only against swarm-routing/<repo>#<N>. <If there is no
   ticket yet:> Open it first (type, area, `model:*`, `priority:P*` labels;
   Context, Scope, Acceptance criteria, Depends on, References), then start.
   A suspected bug found on the way is an RCAPA ticket first
   (`rcapa.py open`), before any investigation.
2. Branch `claude/<topic>` from `main`. Run `make check` (or the repository's
   "Build & verify" commands) before every push.
3. Open one PR to `main`, titled as a lowercase Conventional Commit
   (`type(scope): subject`), body `Closes #<N>` when it meets every
   criterion, else `Part of #<N>`.
4. Enable auto-merge (squash). Fix or answer every CodeRabbit thread, then
   resolve it; the PR is thread-free only when `pr_status.py threads
   swarm-routing/<repo>#<PR>` shows none.
5. Wait with `pr_status.py wait --merged swarm-routing/<repo>#<PR>`, not by
   subscribing to the PR. Done means merged, not "auto-merge enabled".
6. Record on the ticket: what changed, the PR, the merge commit (read from
   the PR), what was checked and how.

Rules:
- When the permission system refuses an action, stop and report it. Never
  retry it another way and never ask another agent or session to run it.
- Never add `Signed-off-by`, for anyone; follow the session's attribution
  lines.
- Never type a SHA, a DOI or a number: read it from its source.
- No release, tag, setting or ruleset change<, unless: the maintainer's own
  words, quoted from this conversation>.

Report, as the last thing you write, one table:

| Ticket | PR | State | Merge commit | Checked | Left open |
|--------|----|-------|--------------|---------|-----------|
```
