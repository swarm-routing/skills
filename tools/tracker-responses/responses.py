#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""How many issues of one label the project acknowledged: the tracker numbers
behind OpenSSF Best Practices' `report_responses` (label bug) and
`enhancement_responses` (label enhancement).

    responses.py OWNER/NAME [--label bug] [--months 2-12] [--today YYYY-MM-DD]
    responses.py --self-test

Counts the issues (not pull requests) with the label created between
`--months` ago (default 12 to 2 months ago, inclusive, as the criteria say)
and classifies each one by who acted on it, from GitHub's own
`author_association` (OWNER, MEMBER or COLLABORATOR is the project):

- acknowledged: filed by the project; or a comment by the project; or closed
  by someone who also commented as the project or filed an issue as the
  project in this set;
- unanswered: no comment and no close by anyone but the reporter;
- unverified: closed by someone whose role this run cannot see (look at it).

Reads the GitHub REST API through `gh api` with explicit `page=` pagination
(`--paginate`'s next links are refused by some proxies). Any failed request,
or more than 100 pages, stops the run with exit 2 and no counts: a partial
count is never printed as a result. Exit 0 otherwise. Read-only.
"""

import argparse
import json
import subprocess
import sys
import urllib.parse
from datetime import date

PROJECT = {"OWNER", "MEMBER", "COLLABORATOR"}
MAX_PAGES = 100


class Incomplete(Exception):
    pass


def gh_get(path):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if p.returncode:
        raise Incomplete(f"GET {path} failed: {p.stderr.strip() or p.stdout.strip()}")
    return json.loads(p.stdout)


def pages(get, path):
    sep = "&" if "?" in path else "?"
    out = []
    for n in range(1, MAX_PAGES + 1):
        batch = get(f"{path}{sep}per_page=100&page={n}")
        if not isinstance(batch, list):
            raise Incomplete(f"GET {path} page {n}: not a list")
        if not batch:
            return out
        out += batch
    raise Incomplete(f"GET {path}: more than {MAX_PAGES} pages")


def months_ago(today, m):
    y, mo = divmod(today.year * 12 + today.month - 1 - m, 12)
    day = min(today.day, 28 if mo + 1 == 2 else 30 if mo + 1 in (4, 6, 9, 11) else 31)
    return date(y, mo + 1, day)


def count(repo, label, lo, hi, get):
    """lo, hi: dates (inclusive). Returns (rows, summary dict)."""
    since = f"{lo.isoformat()}T00:00:00Z"
    q = urllib.parse.urlencode({"state": "all", "labels": label, "since": since})
    issues = [
        i
        for i in pages(get, f"repos/{repo}/issues?{q}")
        if "pull_request" not in i and lo.isoformat() <= i["created_at"][:10] <= hi.isoformat()
    ]
    project_logins = {i["user"]["login"] for i in issues if i.get("author_association") in PROJECT}
    rows = []
    for i in sorted(issues, key=lambda i: i["number"]):
        rep = i["user"]["login"]
        kind = None
        if i.get("author_association") in PROJECT:
            kind = "filed by the project"
        elif i.get("comments", 0):
            for c in pages(get, f"repos/{repo}/issues/{i['number']}/comments"):
                if c["user"]["login"] != rep and c.get("author_association") in PROJECT:
                    kind = "project comment"
                    break
                if c.get("author_association") in PROJECT:
                    project_logins.add(c["user"]["login"])
        if kind is None and i["state"] == "closed":
            closer = ((get(f"repos/{repo}/issues/{i['number']}").get("closed_by")) or {}).get(
                "login"
            )
            if closer and closer != rep and closer in project_logins:
                kind = "closed by the project"
            elif closer and closer != rep:
                kind = "unverified"
        rows.append((i["number"], rep, i.get("author_association", ""), kind or "unanswered"))
    s = {"total": len(rows)}
    for k in ("filed by the project", "project comment", "closed by the project"):
        s[k] = sum(r[3] == k for r in rows)
    s["acknowledged"] = (
        s["filed by the project"] + s["project comment"] + s["closed by the project"]
    )
    s["unanswered"] = sum(r[3] == "unanswered" for r in rows)
    s["unverified"] = sum(r[3] == "unverified" for r in rows)
    return rows, s


def report(repo, label, lo, hi, rows, s):
    lines = [
        f"responses {repo} label={label} created {lo}..{hi}: {s['total']} issue(s); "
        f"acknowledged {s['acknowledged']} (filed by the project {s['filed by the project']}, "
        f"project comment {s['project comment']}, closed by the project {s['closed by the project']}); "
        f"unanswered {s['unanswered']}; unverified {s['unverified']}"
    ]
    who = {}
    for _, rep, assoc, _k in rows:
        who[(rep, assoc)] = who.get((rep, assoc), 0) + 1
    if who:
        lines.append(
            "reporters: " + ", ".join(f"{r} ({a or '?'}) {n}" for (r, a), n in sorted(who.items()))
        )
    for n, rep, _a, k in rows:
        if k in ("unanswered", "unverified"):
            lines.append(f"  #{n} {k} (reporter {rep})")
    q = urllib.parse.quote_plus(f"is:issue label:{label} created:{lo}..{hi}")
    lines.append(f"query: https://github.com/{repo}/issues?q={q}")
    return "\n".join(lines)


def self_test():
    def issue(n, who, assoc, state="open", comments=0, created="2026-03-01T00:00:00Z", pr=False):
        d = {"number": n, "user": {"login": who}, "author_association": assoc, "state": state,
             "comments": comments, "created_at": created}  # fmt: skip
        if pr:
            d["pull_request"] = {}
        return d

    data = {
        "issues": [
            issue(1, "maint", "OWNER"),
            issue(2, "ext", "NONE", comments=2),
            issue(3, "ext", "NONE", comments=1),
            issue(4, "ext", "NONE", state="closed"),
            issue(5, "ext2", "NONE", state="closed"),
            issue(6, "ext", "NONE"),
            issue(7, "ext", "NONE", created="2026-10-30T00:00:00Z"),  # too recent
            issue(8, "maint", "OWNER", pr=True),
        ],
        "comments": {
            2: [
                {"user": {"login": "ext"}, "author_association": "NONE"},
                {"user": {"login": "maint"}, "author_association": "OWNER"},
            ],
            3: [{"user": {"login": "ext"}, "author_association": "NONE"}],
        },  # fmt: skip
        "closed_by": {4: "ext", 5: "stranger"},
    }
    calls = []

    def get(path):
        calls.append(path)
        u = urllib.parse.urlsplit(path)
        qs = urllib.parse.parse_qs(u.query)
        page = int(qs.get("page", ["1"])[0])
        parts = u.path.split("/")
        if parts[-1] == "issues":
            return data["issues"] if page == 1 else []
        if parts[-1] == "comments":
            return data["comments"].get(int(parts[-2]), []) if page == 1 else []
        return {"closed_by": {"login": data["closed_by"][int(parts[-1])]}}

    fails = 0

    def ok(what, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + what)
        fails += not cond

    rows, s = count("o/r", "bug", date(2025, 11, 13), date(2026, 9, 13), get)
    kinds = {r[0]: r[3] for r in rows}
    ok(
        "pull requests and issues outside the window are left out",
        sorted(kinds) == [1, 2, 3, 4, 5, 6],
    )
    ok("an issue the project filed is acknowledged", kinds[1] == "filed by the project")
    ok("a project comment acknowledges", kinds[2] == "project comment")
    ok("the reporter's own comment does not", kinds[3] == "unanswered")
    ok("the reporter closing their own issue does not", kinds[4] == "unanswered")
    ok("a closer whose role is unseen is unverified", kinds[5] == "unverified")
    ok("summary adds up", s["acknowledged"] == 2 and s["unanswered"] == 3 and s["unverified"] == 1)
    ok(
        "pages are asked for explicitly",
        all(
            "page=" in c
            for c in calls
            if "/comments" in c or c.endswith("issues") or "issues?" in c
        ),
    )
    text = report("o/r", "bug", date(2025, 11, 13), date(2026, 9, 13), rows, s)
    ok(
        "report names the query URL",
        "query: https://github.com/o/r/issues?q=is%3Aissue+label%3Abug" in text,
    )

    def failing(path):
        raise Incomplete("GET x failed: HTTP 502")

    try:
        count("o/r", "bug", date(2025, 11, 13), date(2026, 9, 13), failing)
        ok("a failed request stops the count", False)
    except Incomplete:
        ok("a failed request stops the count", True)

    def endless(path):
        return [issue(99, "maint", "OWNER")]

    try:
        pages(endless, "repos/o/r/issues?state=all")
        ok("the page cap stops the count", False)
    except Incomplete:
        ok("the page cap stops the count", True)
    ok("months_ago", months_ago(date(2026, 11, 13), 12) == date(2025, 11, 13)
       and months_ago(date(2026, 3, 31), 1) == date(2026, 2, 28))  # fmt: skip
    print("responses self-test: " + ("OK" if not fails else f"{fails} failure(s)"))
    return 1 if fails else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("repo", nargs="?", metavar="OWNER/NAME")
    p.add_argument("--label", default="bug")
    p.add_argument("--months", default="2-12", help="FROM-TO months ago, inclusive (default 2-12)")
    p.add_argument("--today", help="YYYY-MM-DD (default: today)")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.repo or a.repo.count("/") != 1:
        p.error("OWNER/NAME is required")
    near, far = (int(x) for x in a.months.split("-"))
    today = date.fromisoformat(a.today) if a.today else date.today()
    lo, hi = months_ago(today, far), months_ago(today, near)
    try:
        rows, s = count(a.repo, a.label, lo, hi, gh_get)
    except Incomplete as e:
        print(f"responses: incomplete, no count: {e}", file=sys.stderr)
        return 2
    print(report(a.repo, a.label, lo, hi, rows, s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
