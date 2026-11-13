---
name: fidelity-sheet
description: "Write or update a swarm-routing protocol's paper-fidelity sheet (docs/fidelity.md) — every mechanism and parameter mapped to the paper section that gives it, or marked repo choice / unknown — and the anchor candidate, then check it with tools/fidelity/fidelity.py. Use whenever a protocol or comparator arm needs its fidelity sheet (ARA#4, BeeAdHoc#4, Termite#4, HOPNET#4, any ns3-tools arm), before writing a protocol's core/, when someone asks where a parameter's default comes from, or when reviewing an arm against its paper. Script first: the script checks the shape and the sources; you read the paper with pdf-extract."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/fidelity clones swarm-routing/.github tools/fidelity); reading papers uses the pdf-extract skill of a private library the maintainer keeps.
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

Two paths, set once; you work from the protocol's checkout:

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/fidelity-sheet"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
PAPERS=<checkout>   # a checkout of the private library the maintainer keeps: the papers and the pdf-extract skill
SCRATCH="$(mktemp -d)"   # extracted paper text (step 4); outside every repository
```

`$SKILL/scripts/fidelity` runs `swarm-routing/.github` `tools/fidelity/fidelity.py`
from a cached snapshot. Inside a `.github` checkout,
`python3 tools/fidelity/fidelity.py` is the same; `ORG_TOOLS_DIR=<checkout>`
points the wrapper at a local one.

## The sheet's shape

Four required sections, each a Markdown table (`fidelity.py skeleton` writes them):

| Section | Columns |
|---|---|
| `## Sources` | Key · Citation · Link, generated from `docs/references.bib` (below); a sheet not yet on the bib has Key · Citation · Access (`open`, `browser`, `institution`, `author`, `in hand`) |
| `## Mechanisms` | Mechanism · Source · Implementation · Status |
| `## Parameters` | Parameter · Value · Source · Notes |
| `## Anchor candidate` | Trend · Scenario · Metric · Comparators · Source |

Optional: `## Differences from <arm>` (Paper · Arm · Difference), and any prose.

**The Sources table is the bib's.** `docs/references.bib` is the repository's
one bibliography (swarm-routing/.github#307), and the sheet's keys are its
entry keys: `[G02] §3.2` in a row and `G02` in the bib are one work. The
table sits between `<!-- fidelity:sources:begin -->` and
`<!-- fidelity:sources:end -->` and is rewritten from the bib by
`fidelity bib sources .`; never edit a row of it, and never type a citation,
a DOI or a year: `fidelity bib entry` prints the entry from Crossref's
record. The `references` skill is the whole procedure for the bib (roles, a
work with no DOI, a wrong Crossref record, CITATION.cff); this skill needs
only the three commands in step 3.

A **Source** cell is one of:
- `[KEY] §3.1`, `[KEY] Table 4.1`, `[KEY] Fig. 2`, `[KEY] Listing 13.17`, `[KEY] Alg. 2`, `[KEY] eq. 4.3`, `[KEY] p. 84`, `[KEY] ch. 13` (several joined by `;`, or by `,` after one key). Prefer the narrowest: a page or listing over a whole chapter;
- `repo choice: <why>`: the paper is silent and we picked a value, with the reason (for example "ns-3 AODV's NetTraversalTime, so the reactive arms wait alike");
- `unknown`: the paper is silent and nothing is chosen yet. Its Value is `—`.

**Status** of a mechanism is `as written`, `deviation: <what and why>`, `not implemented: <why>`, or `unknown`.

## 1. Find the paper

The primary source is in the private library the maintainer keeps
(`$PAPERS`; its own README says where each paper is filed), searched with
that library's `pdf-extract` skill. If that library lists the paper only as still to download, it has not
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

If the repo has no `docs/fidelity.md`, start it, then let the bib fill its
Sources table:

```bash
"$SKILL"/scripts/fidelity skeleton --protocol ARA > docs/fidelity.md
DOI=...   # the source's DOI, from its first page (2)
"$SKILL"/scripts/fidelity bib entry "$DOI" --key G02 --role implemented   # prints Crossref's record as a BibTeX entry
# paste the entry into docs/references.bib (2) and put the markers in the sheet (3), then:
"$SKILL"/scripts/fidelity bib sources .                                  # the Sources table, from the bib
```

1. The key is short and stable (first author's initial + year). If
   `docs/references.bib` already holds the work, use its key and skip
   `bib entry`.
2. Take the DOI from the paper's own first page or its publisher's page,
   never from memory. Paste the entry `bib entry` prints into
   `docs/references.bib` as it is (keep the file's header; entries sorted by
   key). It exits 1 when Crossref has no record, or cannot be reached: do
   not write the entry by hand; keep the skeleton's placeholder row and say
   in the PR that the source's entry is missing and why. A work with no DOI (a thesis, a technical report) gets a `url` to
   its institution's or publisher's page: the `references` skill has that
   case.
3. In `docs/fidelity.md`, replace the skeleton's placeholder Sources table
   (the header and its `P1` row) with the two marker lines
   `<!-- fidelity:sources:begin -->` and `<!-- fidelity:sources:end -->`,
   then run `bib sources .`: it writes Key · Citation · Link between them
   and says `Sources table rewritten`.

A second source (a later paper restating the algorithm, the thesis behind
it) is another `bib entry` with its own key and role (`restates`,
`compared`), then `bib sources .` again.

For a sheet that already exists and still has a hand-written Key ·
Citation · Access table, do not convert it in passing: say so in the PR and
leave the move to the bib to the `references` skill.

## 4. Read the paper by grepping it

Do not read the whole PDF into context. Find the structure first, then each mechanism:

```bash
python3 -I "$PAPERS"/.claude/skills/pdf-extract/pdfx.py outline <pdf>   # headings, tables, figures, equations: line and page
python3 -I "$PAPERS"/.claude/skills/pdf-extract/pdfx.py grep <pdf> 'evaporat|pheromone|Table' -C 2
```

`outline` is the map: it skips the table of contents and gives each section,
caption and equation label with its text line and its PDF and printed page,
so you open the right place without reading the paper, and you cite the
section and table numbers it prints rather than ones remembered from another
version.

`outline` needs a papers checkout from 2026-11-09 or later: if `pdfx.py
--help` does not list it, `git -C "$PAPERS" pull` first. Without that, grep
for the structure instead (`pdfx.py grep <pdf> '^(Table|Fig\.|[0-9]+(\.[0-9]+)*) '`)
and check each section number against the text you cite.

(the PDF found in step 1). `pdfx.py text` caches the extracted text
next to the PDF; to keep the papers checkout clean, extract once with
`pdfx.py text <pdf> --out "$SCRATCH/<key>.txt"` and grep that file, or copy
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
"$SKILL"/scripts/fidelity check docs/fidelity.md      # must end "fidelity check: ok"
"$SKILL"/scripts/fidelity verify docs/fidelity.md --text G02="$SCRATCH/g02.txt"   # one --text per source key
"$SKILL"/scripts/fidelity row docs/fidelity.md --protocol ARA
"$SKILL"/scripts/fidelity bib check .                 # must print "fidelity bib check: ok"
```

`bib check` is the sheet against `docs/references.bib`: every `[KEY]` the
sheet cites is an entry, each entry has a `doi` or `url` and a role, and the
Sources table is the bib's. Fix a finding in the bib and run `bib sources .`
again, never in the table. Two sheets from step 3 cannot print `ok` yet: one
that kept the skeleton's placeholder row because Crossref had no record, and
an existing one with a hand-written table. `bib check` then exits 1 with
`no Sources markers` (and each cited key the bib lacks). That finding is
true and stays: copy it into the PR with what is missing, and leave it to
the `references` skill. Do not add markers around a hand-written table or
type an entry to make the check pass.

`$SCRATCH` holds each source's text from step 4 (`pdfx.py text --out`);
add one `--text KEY=PATH` per key in `## Sources` that you have the text of.
`verify` finds the cited places for you. In the Mechanisms and Parameters
tables it checks:

- that each cited section, table or figure exists in that text;
- for a Parameters row citing a table, that the row's value appears in that
  table on a line naming the parameter;
- for an equation, that its label `(N)` is there.

It does not check everything, so a clean run is not a confirmation:

- **A value cited to a section** is only looked for somewhere in that section
  (a `10 ms` row can pass on a `10 nodes`): read the section for the value and
  its unit.
- **Page, chapter and algorithm locators** (`p. 84`, `ch. 13`, `Alg. 2`) and
  the `## Anchor candidate` rows are not verified: check them by hand.
- **Mechanism rows** need reading: no script can tell whether the section
  says what the row claims.

A FAIL means the script did not find the citation or the value where the row
says. Open the paper at that place before changing anything. Extraction can
mislead (a caption printed after its table, a table split across pages). If
the paper holds the value, keep the row and say in the PR which FAIL is an
extraction artefact. If it does not, fix the row (the value is unknown, or
another section gives it), never the text. A WARN that a key was not checked
means a source had no `--text`: give it one, or say in the PR why that source
is not in hand. What `verify` saves is re-reading every table-cited value and
every locator; the reading above stays yours.

`check` names every malformed row. Fix the row, never the checker. Its summary
line lists the unknowns, the repo choices, and the **open** rows: mechanisms
that cite a section but whose Status is `unknown: …` because the section does
not settle them (an ambiguous reading). Mark such a row that way rather than
picking a reading silently. All three lists are the open questions to put in
the PR body and the issue; the open rows are the ones to pre-register before
`core/` (as swarm-routing/ARA#15). `row` prints the one-line summary that the
swarm-protocol review (swarm-routing/.github#54) and the issue comment use.

## 8. Pull request

One PR per repo, titled `docs: fidelity sheet for <protocol> (#N)`. In the body:
- the `check` summary line and the `verify` summary line (locators checked, misses), with each FAIL kept as an extraction artefact and what you checked by hand (section values, pages, chapters, algorithms, the anchor);
- the unknowns, as a checklist for the maintainer;
- the open rows (ambiguous readings), each with the choices and their evidence;
- the anchor candidate.

Close the fidelity issue only when the maintainer has answered the unknowns, or
accepted them as repo choices.
