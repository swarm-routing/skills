---
name: fidelity-sheet
description: Write or update a swarm-routing protocol's paper-fidelity sheet (docs/fidelity.md) — every mechanism and parameter mapped to the paper section that gives it, or marked repo choice / unknown — and the anchor candidate, then check it with tools/fidelity/fidelity.py. Use whenever a protocol or comparator arm needs its fidelity sheet (ARA#4, BeeAdHoc#4, Termite#4, HOPNET#4, any ns3-tools arm), before writing a protocol's core/, when someone asks where a parameter's default comes from, or when reviewing an arm against its paper. Script first: the script checks the shape and the sources; you read the paper with pdf-extract.
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/fidelity clones swarm-routing/.github tools/fidelity); reading papers uses the papers repository's pdf-extract skill.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# fidelity-sheet

A comparator's numbers count only after its fidelity sheet exists (org rule 6,
the first of three gates). The sheet is the record of what the paper actually
says, so the code can be written from the paper and not from an older arm or
from memory. Its value is that every row can be traced: a reviewer must be able
to open the paper at the cited place and find the value there.

`scripts/fidelity` (next to this file) runs `swarm-routing/.github`
`tools/fidelity/fidelity.py` from a cached clone. Inside a `.github` checkout,
`python3 tools/fidelity/fidelity.py` is the same; `ORG_TOOLS_DIR=<checkout>`
points the wrapper at a local one.

## The sheet's shape

Four required sections, each a Markdown table (`fidelity.py skeleton` writes them):

| Section | Columns |
|---|---|
| `## Sources` | Key · Citation · Access (`open`, `browser`, `institution`, `author`, `in hand`) |
| `## Mechanisms` | Mechanism · Source · Implementation · Status |
| `## Parameters` | Parameter · Value · Source · Notes |
| `## Anchor candidate` | Trend · Scenario · Metric · Comparators · Source |

Optional: `## Differences from <arm>` (Paper · Arm · Difference), and any prose.

A **Source** cell is one of:
- `[KEY] §3.1`, `[KEY] Table 4.1`, `[KEY] Fig. 2`, `[KEY] Listing 13.17`, `[KEY] Alg. 2`, `[KEY] eq. 4.3`, `[KEY] p. 84`, `[KEY] ch. 13` (several joined by `;`, or by `,` after one key). Prefer the narrowest: a page or listing over a whole chapter;
- `repo choice: <why>`: the paper is silent and we picked a value, with the reason (for example "ns-3 AODV's NetTraversalTime, so the reactive arms wait alike");
- `unknown`: the paper is silent and nothing is chosen yet. Its Value is `—`.

**Status** of a mechanism is `as written`, `deviation: <what and why>`, `not implemented: <why>`, or `unknown`.

## 1. Find the paper

The primary source is in the private papers library (`swarm-routing/papers`,
`AntHocNet/library/<protocol>/`), searched with that repository's `pdf-extract`
skill. If the paper is only listed in `library/MANUAL-DOWNLOADS.md`, it has not
been downloaded: say so and stop. Downloading a paywalled paper is a human step,
and a sheet written from an abstract or from memory is worse than no sheet,
because it looks authoritative.

Secondary sources (reviews, theses that restate the protocol) get their own key
in `## Sources`. Cite them where they are the only source, and say so in Notes.

## 2. Which version of the protocol?

A thesis or project report often describes the protocol more than once: a formal
model, a revised design, an enhanced variant, an implementation. Their constants
and mechanisms differ. Termite's dissertation has three (ch. 4, ch. 5, ch. 7
ReTermite); the BeeAdHoc PG 460 report has a model with a dance floor (chs. 3–4)
and a Linux module without one (chs. 12–13). Before filling rows:

- list the versions the source describes, with their chapters;
- note which one any existing arm followed, and which one the anchor's
  published comparison used: they are not always the same;
- if the repo's AGENTS.md or an issue already chose one, follow it; otherwise
  say which one each row belongs to (prefix the row, `ch. 4:`), and put the
  choice to the maintainer in the PR. It must be pre-registered in an issue
  before code.

Mixing rows from two versions without saying so is the silent error this sheet
exists to prevent.

## 3. Start the file

If the repo has no `docs/fidelity.md`:

```bash
scripts/fidelity skeleton --protocol ARA --key G02 \
  --citation "M. Güneş, U. Sorges, I. Bouazizi, ARA – The Ant-Colony Based Routing Algorithm for MANETs, ICPP Workshops (IWAHN) 2002, pp. 79–85, DOI 10.1109/ICPPW.2002.1039715" > docs/fidelity.md
```

The key is short and stable (first author's initial + year).

## 4. Read the paper by grepping it

Do not read the whole PDF into context. Find the structure first, then each mechanism:

```bash
python3 .claude/skills/pdf-extract/pdfx.py grep <pdf> '^[0-9IVX]+\.?\s+[A-Z]' -C 0   # section headings
python3 .claude/skills/pdf-extract/pdfx.py grep <pdf> 'evaporat|pheromone|Table' -C 2
```

(the PDF path is the library path). `pdfx.py text` caches the extracted text
next to the PDF; to keep the papers checkout clean, extract once with
`pdfx.py text <pdf> --out <scratch>/<name>.txt` and grep that file, or copy
the PDF to a scratch directory first. For each
mechanism the paper describes, write one Mechanisms row with the locator where
it is defined. For each constant, write one Parameters row:

- **Value given in the paper** → the value and its locator, exactly as written,
  with units.
- **Value not given** → `unknown` and `—`. Do not fill it from the old arm, a
  review, or a plausible default: that is how arms drift from their paper. If
  the implementation needs a number anyway, that is a `repo choice: <why>`
  row, chosen deliberately and said out loud.
- **The paper is ambiguous** (two readings) → the reading you take goes in
  Notes, and the alternative goes into the issue for the maintainer
  (BeeAdHoc golden rule 11: interpretations are pre-registered in an issue
  before code).

Quote at most a sentence or a formula, attributed. The protocol repos are
public; the paper's text is not ours to copy.

## 5. Compare with the existing arm

When the protocol already exists as an AntHocNet comparator arm
(`ns3/baselines/adaptive/README.md` in `swarm-routing/AntHocNet` carries those
arms' sheets) or in ns3-tools, add `## Differences from <arm>` with one row per
difference: what the paper says, what the arm does, and the consequence. That
list is what the fresh implementation must not inherit by accident.

## 6. The anchor candidate

One row: the paper's headline trend, as a testable rule (metric, direction,
the conditions compared), the scenario it was measured in (nodes, area,
mobility, traffic, duration), and the comparators. Note whether the org can
reproduce it with the arms it has (AODV, OLSR, DSDV, AntHocNet, …). If the
paper reports nothing reproducible, write `none: <why>`. The protocol then
ships as an infeasibility verdict, not as numbers.

## 7. Check, then summarise

```bash
scripts/fidelity check docs/fidelity.md      # must end "fidelity check: ok"
scripts/fidelity row docs/fidelity.md --protocol ARA
```

`check` names every malformed row. Fix the row, never the checker. Its summary
line lists the unknowns and repo choices: those are the open questions to
put in the PR body and the issue. `row` prints the one-line summary that the
swarm-protocol review (swarm-routing/.github#54) and the issue comment use.

## 8. Pull request

One PR per repo, titled `docs: fidelity sheet for <protocol> (#N)`. In the body:
- the `check` summary line;
- the unknowns, as a checklist for the maintainer;
- any ambiguous readings;
- the anchor candidate.

Close the fidelity issue only when the maintainer has answered the unknowns, or
accepted them as repo choices.
