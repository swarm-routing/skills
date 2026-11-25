# Roadmap

Which release each piece of work serves, and what each release must show to
ship. Releases are cut on the maintainer's request only (swarm-routing/.github
CONTRIBUTING "Cutting a release"); the org-wide view is the
[org ROADMAP](https://github.com/swarm-routing/.github/blob/main/ROADMAP.md).
A version's scope is the set of issues labelled `release:vX.Y.Z`; the release
workflow's ladder gate refuses a bump whose version has no row here.

The plugin published versions before it had tags: `plugin.json` is bumped in
every plugin PR (golden rule 12), and the first tag continues that numbering
instead of starting at 0.1.0 (maintainer decision on
[swarm-routing/.github#636](https://github.com/swarm-routing/.github/issues/636),
2026-11-17). Commitizen bumps the release from the version `plugin.json` holds
then, so if plugin PRs have moved it past 0.32.x when the release is
requested, the dry run's version replaces the one below in a PR first.

## Release ladder

| Release | Theme | Exit criteria |
|---|---|---|
| v0.35.0 | first tagged release (requested by the maintainer 2026-11-22: "release swarm-mcp v0.1.0 and skills"); the plugin's swarm-mcp pinned to the swarm-mcp v0.1.0 release | `release.yml` on `reusable-release.yml` with `first-release-from-config`; `.cz.toml`, `plugin.json`, the marketplace entry and `CITATION.cff` at one version (`make test`); `swarm-mcp.lock` names swarm-mcp's v0.1.0 tag and the commit it names; a dry run green; no open issue labelled `release:v0.35.0`; the maintainer asks for it |
| v0.35.2 | patch release (requested by the maintainer 2026-11-25): the fixes since v0.35.0 (#200, #205) and the plugin changes that moved the version files to 0.35.1 unreleased; the version Commitizen computes from them | #200 and #205 merged; `make check` green on `main`; the dry run computes 0.35.2; no open issue labelled `release:v0.35.2`; the maintainer asks for it |

## Non-goals

- No scheduled or per-change release: a plugin change reaches sessions from
  `main` without one, and a release is the citable, verifiable snapshot.

## Shipped releases

Every published release (no Zenodo archive: `zenodo = false`), read from GitHub by swarm-routing/.github `tools/zenodo/zenodo.py shipped` (org-bot's `release-aftercare` task); never edit the block by hand.

<!-- releases:shipped:begin (zenodo.py shipped --write; never edit by hand) -->
- **v0.35.2** shipped 2026-11-25 ([release](https://github.com/swarm-routing/skills/releases/tag/v0.35.2))
- **v0.35.0** shipped 2026-11-22 ([release](https://github.com/swarm-routing/skills/releases/tag/v0.35.0))
<!-- releases:shipped:end -->
