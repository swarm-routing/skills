#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Run the script graders of a skill's evals against an eval workspace.

    grade.py WORKSPACE [--evals DIR] [--write]
    grade.py --self-test

A case's graders are skills/<skill>/evals/<case>/graders/*: an `NN.md` is an
LLM grader (frontmatter `type: llm`, judged by a model, as before) and an
`NN.sh` is a script grader, for the criteria a script can decide ("check_docs.py
passes", "no stub file was created", "the badge block is unchanged"). A script
grader is an executable whose header names its criterion:

    # grader: The fixed docs/fidelity.md passes fidelity.py check (it prints
    #   'fidelity check: ok').

(continuation lines start with `#` and two spaces). It runs as
`NN.sh REPO OUTPUTS` from OUTPUTS, where REPO is the run's edited fixture
repository and OUTPUTS its outputs directory (either may be missing; the
grader decides). Exit 0 is a pass, 77 means it cannot grade this run (an input
it needs is missing), anything else is a fail; the tail of its output is the
evidence. `claude plugin eval` reads only graders/*.md, so a .sh grader does
not disturb it (an .md with an unknown `type` would make the case fail to load).

WORKSPACE is a skill-creator iteration directory: <case>/<config>/ holding
repo/ and outputs/ (or <case>/<config>/run-N/ when there are several runs).
The case is found by name under DIR (default: every skills/*/evals/ in this
repository). One line per grader and run: PASS, FAIL, SKIP (exit 77), or
JUDGE for an LLM grader, which this script leaves to the judge. When the run
already has a grading.json with an entry of the same text (the hand grade),
the line shows whether the script agrees. --write merges the script results
into each run's grading.json in the skill-creator shape (`expectations`
{text, passed, evidence}, `summary` {passed, failed, total, pass_rate}): an
entry with the same text is replaced, others are kept, the summary is
recomputed. Run it after the LLM grading, so the judge's file is merged into
rather than overwritten. Exit 0 whatever the grades; 2 on a usage error.

Graders that call the org tools go through the skills' wrappers, which fetch
swarm-routing/.github; ORG_TOOLS_DIR=<checkout> (and ORG_SYNC_DIR for org-sync)
grades offline. Stdlib only.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP = 77
TIMEOUT = 600
EVIDENCE_LINES = 3  # the tail of a grader's output kept as evidence
EVIDENCE_WIDTH = 120  # characters kept of each of those lines


def criterion(path):
    """The text after `# grader:` and its `#  ` continuation lines, or None."""
    text, on = [], False
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not on:
                m = re.match(r"#\s*grader:\s*(.*)", line)
                if m:
                    on = True
                    text.append(m.group(1).strip())
            elif re.match(r"#\s{2,}\S", line):
                text.append(line[1:].strip())
            else:
                break
    return " ".join(text) if text else None


def md_body(path):
    """(frontmatter type, body) of a grader .md."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text.strip()
    t = re.search(r"^type:\s*(\S+)", m.group(1), re.M)
    return (t.group(1) if t else None), m.group(2).strip()


def graders(case_dir):
    """[(name, kind, text, path)] in file order; kind 'script' or the .md type."""
    gdir = os.path.join(case_dir, "graders")
    out = []
    for name in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
        path = os.path.join(gdir, name)
        if name.endswith(".sh"):
            out.append((name, "script", criterion(path) or name, path))
        elif name.endswith(".md"):
            kind, body = md_body(path)
            out.append((name, kind or "llm", body, path))
    return out


def norm(text):
    return " ".join(text.split())


def run_dirs(workspace):
    """[(case, run_dir)]: every <case>/<config>[/run-N] holding repo/, outputs/ or grading.json."""

    def holds(d):
        return any(os.path.exists(os.path.join(d, x)) for x in ("repo", "outputs", "grading.json"))

    out = []
    for case in sorted(os.listdir(workspace)):
        cdir = os.path.join(workspace, case)
        if not os.path.isdir(cdir):
            continue
        name = case
        meta = os.path.join(cdir, "eval_metadata.json")
        if os.path.isfile(meta):
            with open(meta, encoding="utf-8") as f:
                name = json.load(f).get("eval_name", case)
        for config in sorted(os.listdir(cdir)):
            kdir = os.path.join(cdir, config)
            if not os.path.isdir(kdir):
                continue
            runs = sorted(
                os.path.join(kdir, r)
                for r in os.listdir(kdir)
                if r.startswith("run-") and os.path.isdir(os.path.join(kdir, r))
            )
            out.extend((name, r) for r in runs or ([kdir] if holds(kdir) else []))
    return out


def find_case(name, evals):
    hits = [os.path.join(e, name) for e in evals if os.path.isdir(os.path.join(e, name))]
    return hits[0] if len(hits) == 1 else None


def run_script(path, run_dir):
    run_dir = os.path.abspath(run_dir)
    repo, outputs = os.path.join(run_dir, "repo"), os.path.join(run_dir, "outputs")
    cwd = outputs if os.path.isdir(outputs) else run_dir
    try:
        p = subprocess.run(
            [os.path.abspath(path), repo, outputs],
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        code, out = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        code, out = 1, f"timed out after {TIMEOUT} s"
    except OSError as e:
        code, out = 1, f"cannot run: {e}"
    lines = [ln.rstrip() for ln in out.strip().splitlines() if ln.strip()]
    tail = [ln if len(ln) <= EVIDENCE_WIDTH else ln[: EVIDENCE_WIDTH - 1] + "…" for ln in lines]
    evidence = " / ".join(tail[-EVIDENCE_LINES:]) or f"exit {code}"
    return code, evidence


def load_grading(run_dir):
    path = os.path.join(run_dir, "grading.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def merge(grading, results):
    """grading.json dict with the script results merged in by text."""
    exps = [e for e in grading.get("expectations", []) if isinstance(e, dict)]
    index = {norm(e.get("text", "")): i for i, e in enumerate(exps)}
    for text, passed, evidence in results:
        entry = {"text": text, "passed": passed, "evidence": evidence}
        if norm(text) in index:
            exps[index[norm(text)]] = entry
        else:
            index[norm(text)] = len(exps)
            exps.append(entry)
    passed = sum(1 for e in exps if e.get("passed") is True)
    total = len(exps)
    grading["expectations"] = exps
    grading["summary"] = {
        **(grading.get("summary") if isinstance(grading.get("summary"), dict) else {}),
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
    }
    return grading


def grade(workspace, evals, write=False, out=print):
    """Grade every run; returns the counts."""
    counts = {"pass": 0, "fail": 0, "skip": 0, "judge": 0, "agree": 0, "differ": 0}
    runs = run_dirs(workspace)
    if not runs:
        out(f"grade: no runs under {workspace} (<case>/<config>/ with repo/ or outputs/)")
    for name, run_dir in runs:
        case_dir = find_case(name, evals)
        out(os.path.relpath(run_dir, workspace))
        if case_dir is None:
            out(f"  ?      no unique eval case `{name}` under {', '.join(evals)}")
            continue
        hand = {
            norm(e.get("text", "")): e.get("passed")
            for e in load_grading(run_dir).get("expectations", [])
            if isinstance(e, dict)
        }
        results = []
        for gname, kind, text, path in graders(case_dir):
            if kind != "script":
                counts["judge"] += 1
                out(f"  JUDGE  {gname}  ({kind}) {text[:90]}")
                continue
            code, evidence = run_script(path, run_dir)
            if code == SKIP:
                counts["skip"] += 1
                out(f"  SKIP   {gname}  {evidence}")
                continue
            passed = code == 0
            counts["pass" if passed else "fail"] += 1
            note = ""
            if norm(text) in hand:
                same = hand[norm(text)] is passed
                counts["agree" if same else "differ"] += 1
                note = "  [agrees with grading.json]" if same else "  [DIFFERS from grading.json]"
            out(f"  {'PASS' if passed else 'FAIL'}   {gname}  {evidence}{note}")
            results.append((text, passed, evidence))
        if write and results:
            merged = merge(load_grading(run_dir), results)
            with open(os.path.join(run_dir, "grading.json"), "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
                f.write("\n")
    compared = counts["agree"] + counts["differ"]
    out(
        f"grade: {len(runs)} run(s); script graders {counts['pass']} passed, "
        f"{counts['fail']} failed, {counts['skip']} skipped; "
        f"{counts['judge']} need judgement"
        + (f"; {counts['agree']} of {compared} agree with grading.json" if compared else "")
    )
    return counts


def self_test():
    failures = []

    def expect(what, ok):
        print(("ok    " if ok else "FAIL  ") + what)
        if not ok:
            failures.append(what)

    tmp = tempfile.mkdtemp()
    try:
        case = os.path.join(tmp, "evals", "demo")
        os.makedirs(os.path.join(case, "graders"))

        def put(rel, text, mode=0o644):
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
            os.chmod(p, mode)

        put("evals/demo/graders/01.md", "---\ntype: llm\nweight: 1\n---\n\nThe report is short.\n")
        put(
            "evals/demo/graders/02.sh",
            "#!/bin/sh\n# grader: The repo has a docs/README.md\n#   (a docs map).\n"
            'test -f "$1/docs/README.md" && echo "found docs/README.md"\n',
            0o755,
        )
        put(
            "evals/demo/graders/03.sh",
            '#!/bin/sh\n# grader: The report names the fix.\ngrep -q fix "$2/report.md" '
            '|| { echo "report.md: no fix"; exit 1; }\n',
            0o755,
        )
        put(
            "evals/demo/graders/04.sh",
            '#!/bin/sh\n# grader: The diff is small.\n[ -f "$2/diff.patch" ] '
            '|| { echo "no diff.patch"; exit 77; }\n',
            0o755,
        )
        expect(
            "criterion reads the header and its continuation",
            criterion(os.path.join(case, "graders/02.sh"))
            == "The repo has a docs/README.md (a docs map).",
        )
        ws = os.path.join(tmp, "ws")
        good = os.path.join(ws, "demo", "with_skill")
        put("ws/demo/with_skill/repo/docs/README.md", "# docs\n")
        put("ws/demo/with_skill/outputs/report.md", "the fix: done\n")
        put("ws/demo/without_skill/run-1/outputs/report.md", "nothing\n")
        put("ws/demo/eval_metadata.json", json.dumps({"eval_name": "demo"}))
        hand = {
            "expectations": [
                {"text": "The report is short.", "passed": True, "evidence": "3 lines"},
                {
                    "text": "The repo has a  docs/README.md (a docs map).",
                    "passed": False,
                    "evidence": "x",
                },
            ],
            "summary": {"passed": 1, "failed": 1, "total": 2, "pass_rate": 0.5},
            "timing": {"total_duration_seconds": 1.0},
        }
        put("ws/demo/with_skill/grading.json", json.dumps(hand))
        lines = []
        counts = grade(ws, [os.path.join(tmp, "evals")], write=True, out=lines.append)
        text = "\n".join(lines)
        expect("one line per grader and run", text.count("  JUDGE  01.md") == 2)
        expect(
            "a passing script is PASS with its output as evidence",
            "PASS   02.sh  found docs/README.md" in text,
        )
        expect("a failing script is FAIL", "FAIL   03.sh  report.md: no fix" in text)
        expect("exit 77 is SKIP", "SKIP   04.sh  no diff.patch" in text)
        expect("a hand grade that differs is flagged", "DIFFERS from grading.json" in text)
        expect(
            "the counts",
            (counts["pass"], counts["fail"], counts["skip"], counts["judge"], counts["differ"])
            == (2, 2, 2, 2, 1),
        )
        expect("the summary line", lines[-1].startswith("grade: 2 run(s); script graders 2 passed"))
        with open(os.path.join(good, "grading.json"), encoding="utf-8") as f:
            g = json.load(f)
        texts = [e["text"] for e in g["expectations"]]
        expect(
            "--write replaces the same text, keeps the judge's entry, appends the rest",
            texts
            == [
                "The report is short.",
                "The repo has a docs/README.md (a docs map).",
                "The report names the fix.",
            ],
        )
        expect(
            "every entry has text, passed, evidence",
            all({"text", "passed", "evidence"} <= set(e) for e in g["expectations"]),
        )
        expect(
            "the summary is recomputed in the skill-creator shape",
            g["summary"] == {"passed": 3, "failed": 0, "total": 3, "pass_rate": 1.0},
        )
        expect("other keys are kept", g.get("timing") == {"total_duration_seconds": 1.0})
        run1 = os.path.join(ws, "demo", "without_skill", "run-1", "grading.json")
        with open(run1, encoding="utf-8") as f:
            g1 = json.load(f)
        expect(
            "a run without grading.json gets one from the script results",
            g1["summary"] == {"passed": 0, "failed": 2, "total": 2, "pass_rate": 0.0},
        )
        lines = []
        grade(os.path.join(tmp, "evals"), [os.path.join(tmp, "evals")], out=lines.append)
        expect("a directory without runs says so", "no runs under" in lines[0])
        lines = []
        put("ws2/other/with_skill/outputs/report.md", "x\n")
        grade(os.path.join(tmp, "ws2"), [os.path.join(tmp, "evals")], out=lines.append)
        expect(
            "an unknown case is reported", any("no unique eval case `other`" in ln for ln in lines)
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"grade self-test: {'FAILED' if failures else 'OK'}")
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("workspace", nargs="?", help="a skill-creator iteration directory")
    ap.add_argument(
        "--evals",
        action="append",
        help="directory holding the eval cases (repeatable; default: every skills/*/evals/)",
    )
    ap.add_argument("--write", action="store_true", help="merge the results into each grading.json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.workspace or not os.path.isdir(a.workspace):
        ap.error("WORKSPACE must be a directory")
    evals = a.evals or sorted(
        os.path.join(ROOT, "skills", s, "evals")
        for s in os.listdir(os.path.join(ROOT, "skills"))
        if os.path.isdir(os.path.join(ROOT, "skills", s, "evals"))
    )
    grade(a.workspace, evals, write=a.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
