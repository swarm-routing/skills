# RCAPA: does not apply to swarm-routing/skills's own changes

An **RCAPA** (root cause analysis with corrective and preventive actions) is
required for a regression in a **published library**: a version another
project consumes (a swarm-core or ns3-tools release through its lock or PyPI,
a protocol core's vcpkg port), and for every upstream ns-3 bug. The rule and
its decision table are in [CONTRIBUTING.md, "RCAPA"](https://github.com/swarm-routing/.github/blob/main/CONTRIBUTING.md#rcapa) ([ADR-0003](https://github.com/swarm-routing/.github/blob/main/docs/adr/0003-rcapa-for-ns3-bugs-and-released-regressions.md)).

**RCAPA does not apply to this repository's own changes**, because
nothing consumes it at a version that this rule counts: the plugin
`swarm-routing` installs from `main` by its `plugin.json` version, and its
skills are procedures over scripts in other repositories. A broken skill is
an ordinary `bug` issue, fixed with a plugin version bump.

**Where RCAPA applies instead:** a defect in a script a skill calls lives with that script (mostly
swarm-routing/.github `tools/`, which takes no RCAPA either; ns3-tools' CLI
does, as a library).

The "open RCAPA" badge in the README counts this repository's open issues
labelled `rcapa`, so it reads 0 here.
