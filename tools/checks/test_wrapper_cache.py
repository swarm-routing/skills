#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Self-test for the cached-checkout block every skills/*/scripts/* wrapper
carries: the wrappers run against local bare repositories (SWARM_ROUTING_GIT)
with two refs, concurrently, and a tool that is running keeps its files while
another session moves the same ref. Needs git, tar and bash; no network.

Cases:
  - four wrappers start at once on an empty cache (with flock, and again with
    no flock on PATH, the mkdir lock): all succeed, each ref in its own dir;
  - a tool started on `main` keeps reading the commit it started from while a
    second wrapper fetches a newer `main` and runs it, and a third runs `other`;
  - the snapshot is not a git checkout and lives in a per-ref directory;
  - token-audit installed alone (skills.sh layout) falls back to its last
    snapshot when the fetch fails; an org-tools wrapper fails instead.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W = {
    "fidelity": os.path.join(ROOT, "skills/fidelity-sheet/scripts/fidelity"),
    "org-tool": os.path.join(ROOT, "skills/references/scripts/org-tool"),
    "lit-search": os.path.join(ROOT, "skills/lit-search/scripts/lit-search"),
    "org-sync": os.path.join(ROOT, "skills/org-repo/scripts/org-sync"),
}

# The fake tool: prints its data file, optionally after waiting for a go file,
# so the test can move the ref while it runs.
TOOL = """import os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
if args and args[0] == "wait":
    open(args[1], "w").close()
    while not os.path.exists(args[2]):
        time.sleep(0.05)
print(open(os.path.join(here, "data.txt")).read().strip(), here)
"""

failed = 0


def check(cond, what):
    global failed
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        failed += 1


def git(cwd, *args):
    subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True)


def commit(work, files, msg):
    for path, text in files.items():
        p = os.path.join(work, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    git(work, "add", "-A")
    git(work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", msg)


def remote(base, name, tools):
    """A bare repo base/name holding each tool beside a data.txt: "A" on
    branch main, "OTHER" on branch other."""
    work = os.path.join(base, "work-" + name)
    git(base, "init", "-q", "-b", "main", work)

    def data(text):
        return {os.path.join(os.path.dirname(t), "data.txt"): text for t in tools}

    commit(work, {**{t: TOOL for t in tools}, **data("A")}, "A")
    git(work, "checkout", "-qb", "other")
    commit(work, data("OTHER"), "other")
    git(work, "checkout", "-q", "main")
    bare = os.path.join(base, "remote", name)
    git(base, "clone", "-q", "--bare", work, bare)
    git(work, "remote", "add", "origin", bare)
    return work


def env_for(base, cache, path=None, **extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith(("ORG_", "SKILLS_TOOLS"))}
    e.update(XDG_CACHE_HOME=cache, SWARM_ROUTING_GIT="file://" + base + "/remote")
    if path is not None:
        e["PATH"] = path
    e.update(extra)
    return e


def run_all(cmds, env):
    procs = [
        subprocess.Popen(
            c, env={**env, **e}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for c, e in cmds
    ]
    return [(p.wait(), *p.communicate()) for p in procs]


def no_flock_path(base):
    """A PATH with every command the wrappers use, and no flock."""
    d = os.path.join(base, "bin-noflock")
    os.makedirs(d)
    for cmd in (
        "git",
        "tar",
        "mktemp",
        "mkdir",
        "find",
        "touch",
        "cat",
        "tr",
        "seq",
        "sleep",
        "rm",
        "rmdir",
        "mv",
        "dirname",
        "python3",
        "bash",
        "env",
    ):
        src = shutil.which(cmd)
        assert src, cmd
        os.symlink(src, os.path.join(d, cmd))
    return d


def main():
    for tool in ("git", "tar", "bash"):
        if not shutil.which(tool):
            print(f"skip  {tool} not found")
            return 0
    base = tempfile.mkdtemp(prefix="wrapper-cache-")
    try:
        org = remote(
            base,
            ".github",
            [
                "tools/fidelity/fidelity.py",
                "tools/lit-search/lit_search.py",
                "tools/org-sync/org_sync.py",
            ],
        )
        remote(base, "skills", ["tools/token-audit/token_audit.py"])

        for label, path in (("flock", None), ("mkdir lock (no flock)", no_flock_path(base))):
            cache = os.path.join(base, "cache-" + label.split()[0])
            env = env_for(base, cache, path)
            res = run_all(
                [
                    ([W["fidelity"]], {}),
                    ([W["org-tool"], "fidelity"], {}),
                    ([W["lit-search"]], {"ORG_TOOLS_REF": "other"}),
                    ([W["org-sync"]], {"ORG_SYNC_REF": "other"}),
                ],
                env,
            )
            outs = [o.split()[0] if o else "" for _, o, _ in res]
            check(
                all(rc == 0 for rc, _, _ in res) and outs == ["A", "A", "OTHER", "OTHER"],
                f"{label}: four wrappers at once on an empty cache, two refs: {outs}"
                + "".join(f"\n      {e.strip()}" for rc, _, e in res if rc),
            )
            dirs = sorted(os.listdir(os.path.join(cache, "swarm-routing/checkouts/github")))
            check(dirs == ["main", "other"], f"{label}: one cache dir per ref: {dirs}")

        # A running tool keeps its commit while main moves under it.
        cache = os.path.join(base, "cache-race")
        env = env_for(base, cache)
        started, go = os.path.join(base, "started"), os.path.join(base, "go")
        first = subprocess.Popen(
            [W["fidelity"], "wait", started, go],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 60
        while not os.path.exists(started) and first.poll() is None and time.time() < deadline:
            time.sleep(0.05)
        check(os.path.exists(started), "the first tool is running on main@A")
        commit(org, {"tools/fidelity/data.txt": "B"}, "B")
        git(org, "push", "-q", "origin", "main")
        res = run_all(
            [([W["org-tool"], "fidelity"], {}), ([W["lit-search"]], {"ORG_TOOLS_REF": "other"})],
            env,
        )
        open(go, "w").close()
        out1, err1 = first.communicate(timeout=60)
        check(
            res[0][0] == 0 and res[0][1].startswith("B "),
            f"a second session fetches main@B and runs it: {res[0][1].strip()!r}",
        )
        check(
            res[1][0] == 0 and res[1][1].startswith("OTHER "),
            f"a third session runs `other` meanwhile: {res[1][1].strip()!r}",
        )
        check(
            first.returncode == 0 and out1.startswith("A "),
            f"the first tool still reads main@A after the update: {out1.strip()!r} {err1.strip()}",
        )
        snap_a, snap_b = out1.split()[1], res[0][1].split()[1]
        snap = os.path.dirname(os.path.dirname(snap_b))  # <cache>/<ref>/<sha>
        check(
            snap_a != snap_b
            and os.path.basename(os.path.dirname(snap)) == "main"
            and not os.path.exists(os.path.join(snap, ".git")),
            f"each commit is its own snapshot under the ref's dir, not a git checkout: {snap}",
        )

        # token-audit installed alone: offline falls back to the last snapshot.
        alone = os.path.join(base, "installed/token-audit/scripts")
        os.makedirs(alone)
        shutil.copy(os.path.join(ROOT, "skills/token-audit/scripts/token-audit"), alone)
        ta = os.path.join(alone, "token-audit")
        env = env_for(base, os.path.join(base, "cache-ta"))
        r1 = subprocess.run([ta], env=env, capture_output=True, text=True)
        check(
            r1.returncode == 0 and r1.stdout.startswith("A "),
            f"token-audit installed alone fetches its tool: {r1.stdout.strip()!r} {r1.stderr.strip()}",
        )
        env["SWARM_ROUTING_GIT"] = "file://" + base + "/nowhere"
        r2 = subprocess.run([ta], env=env, capture_output=True, text=True)
        check(
            r2.returncode == 0 and r2.stdout.startswith("A ") and "could not refresh" in r2.stderr,
            f"token-audit offline uses its last snapshot and says so: {r2.stderr.strip()!r}",
        )
        env["XDG_CACHE_HOME"] = os.path.join(base, "cache-race")
        r3 = subprocess.run([W["fidelity"]], env=env, capture_output=True, text=True)
        check(r3.returncode != 0, "an org-tools wrapper fails when the fetch fails")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"test_wrapper_cache: {failed} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
