#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Self-test for tools/mcp/swarm-mcp, the launcher the plugin's .mcp.json runs:
it starts swarm-routing/swarm-mcp's server at the commit swarm-mcp.lock pins,
here from a local bare repository (SWARM_ROUTING_GIT) holding a stub server.
Needs git, tar and bash; no network.

Cases:
  - the pinned commit runs, with the launcher's arguments, and the snapshot
    is the pinned commit's even after the remote's main moves on;
  - with the remote gone, the cached snapshot of the pin still serves
    (offline-ok), and a pin never fetched fails with nothing on stdout;
  - SWARM_MCP_DIR runs that checkout instead of the pin;
  - a lock without a 40-hex commit fails with nothing on stdout (stdout is the
    MCP stream).
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LAUNCHER = os.path.join(ROOT, "tools", "mcp", "swarm-mcp")
STUB = "import sys\nprint({!r}, *sys.argv[1:])\n"

failed = 0


def check(cond, what):
    global failed
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        failed += 1


def git(cwd, *args):
    return subprocess.run(
        ["git", "-C", cwd, *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def commit(work, tag):
    p = os.path.join(work, "tools", "swarm-mcp", "swarm_mcp.py")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(STUB.format(tag))
    git(work, "add", "-A")
    git(work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", tag)
    return git(work, "rev-parse", "HEAD")


def plugin(base, lock_text):
    """A plugin tree holding the launcher and a swarm-mcp.lock."""
    d = tempfile.mkdtemp(dir=base)
    os.makedirs(os.path.join(d, "tools", "mcp"))
    shutil.copy(LAUNCHER, os.path.join(d, "tools", "mcp", "swarm-mcp"))
    with open(os.path.join(d, "swarm-mcp.lock"), "w") as f:
        f.write(lock_text)
    return os.path.join(d, "tools", "mcp", "swarm-mcp")


def lock(sha):
    return f'repository = "swarm-routing/swarm-mcp"\ncommit = "{sha}"\n'


def run(launcher, env, *args):
    p = subprocess.run(
        ["bash", launcher, *args], env=env, capture_output=True, text=True, timeout=120
    )
    return p.returncode, p.stdout.strip(), p.stderr


def main():
    base = tempfile.mkdtemp(prefix="mcp-launcher-")
    try:
        work = os.path.join(base, "work")
        git(base, "init", "-q", "-b", "main", work)
        first = commit(work, "FIRST")
        bare = os.path.join(base, "remote", "swarm-mcp")
        git(base, "clone", "-q", "--bare", work, bare)
        git(work, "remote", "add", "origin", bare)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("SWARM_", "ORG_"))}
        env.update(
            XDG_CACHE_HOME=os.path.join(base, "cache"),
            SWARM_ROUTING_GIT="file://" + os.path.join(base, "remote"),
        )

        launcher = plugin(base, lock(first))
        rc, out, err = run(launcher, env, "--self-test")
        check(
            rc == 0 and out == "FIRST --self-test", f"the pinned commit runs ({rc} {out!r} {err})"
        )

        commit(work, "SECOND")
        git(work, "push", "-q", "origin", "main")
        rc, out, _ = run(launcher, env)
        check(rc == 0 and out == "FIRST", "the pin, not the remote's newer main, runs")
        snap = os.path.join(base, "cache", "swarm-routing", "checkouts", "swarm-mcp", first, first)
        check(
            os.path.isfile(os.path.join(snap, "tools", "swarm-mcp", "swarm_mcp.py"))
            and not os.path.exists(os.path.join(snap, ".git")),
            "the snapshot lives in the cache under the pinned commit, not a git checkout",
        )

        shutil.rmtree(os.path.join(base, "remote"))
        rc, out, err = run(launcher, env)
        check(
            rc == 0 and out == "FIRST" and "using the cached" in err,
            "with the remote gone, the cached snapshot of the pin serves",
        )
        never = plugin(base, lock("0" * 40))
        rc, out, _ = run(never, env)
        check(rc != 0 and out == "", "a pin never fetched, offline, fails with no stdout")

        local = os.path.join(base, "local")
        os.makedirs(os.path.join(local, "tools", "swarm-mcp"))
        with open(os.path.join(local, "tools", "swarm-mcp", "swarm_mcp.py"), "w") as f:
            f.write(STUB.format("LOCAL"))
        rc, out, _ = run(never, {**env, "SWARM_MCP_DIR": local}, "--list")
        check(rc == 0 and out == "LOCAL --list", "SWARM_MCP_DIR runs that checkout")

        bad = plugin(base, 'repository = "swarm-routing/swarm-mcp"\ncommit = "main"\n')
        rc, out, err = run(bad, env)
        check(
            rc == 1 and out == "" and "no commit" in err,
            "a lock without a 40-hex commit fails with no stdout",
        )
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"mcp launcher self-test: {'ok' if not failed else f'{failed} failed'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
