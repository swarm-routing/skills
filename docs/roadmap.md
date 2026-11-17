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
| v0.33.0 | first tagged release | `release.yml` on `reusable-release.yml` with `first-release-from-config`; `.cz.toml`, `plugin.json`, the marketplace entry and `CITATION.cff` at one version (`make test`); a dry run green; no open issue labelled `release:v0.33.0`; the maintainer asks for it |

## Non-goals

- No scheduled or per-change release: a plugin change reaches sessions from
  `main` without one, and a release is the citable, verifiable snapshot.
