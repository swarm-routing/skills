---
name: references
description: "Review and set up a swarm-routing repository's bibliography, docs/references.bib: find every paper, thesis, dataset and org release the repository relies on, confirm each from Crossref or Zenodo, write the entries with their fidelity keys and a role, then regenerate the fidelity Sources table and CITATION.cff references from the bib and check them. Use whenever a repository needs its references.bib (epic swarm-routing/.github#307 and its per-repo tickets), a paper is added to or dropped from a fidelity sheet, a README or doc cites a work by hand, CITATION.cff references look stale, someone asks which papers an implementation follows or how to cite them, or a reference shows a bare URL where a DOI exists. Script first: the scripts fetch every field; you never type a DOI, author or title from memory."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/org-tool clones swarm-routing/.github tools/), api.crossref.org and zenodo.org.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# references

Every implementation in the org rests on papers, and a reader must be able to
go from the code to the exact work it follows. `docs/references.bib` is the one
place a repository records those works (swarm-routing/.github#307). Everything
else that lists them is generated from it: the fidelity sheet's Sources table,
`CITATION.cff` `references:`, the README's citing section and the site's
project page. A hand-typed copy drifts and a field typed from memory is wrong
often enough to matter, so the scripts write the fields and you decide what
belongs and why.

Set once, then work from the repository's checkout:

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/references"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
T="$SKILL/scripts/org-tool"    # T fidelity|lit-search|zenodo|org-sync ...
```

`ORG_TOOLS_DIR=<checkout of swarm-routing/.github>` points the wrapper at a
local checkout instead of the cached clone.

## The rules the scripts enforce, and why

- **DOI links first.** A reference with a DOI is shown as its
  `https://doi.org/<DOI>` link everywhere: the link survives publisher
  moves, and a reader lands on the version of record. `url` is for a work
  with no DOI (a thesis in a university repository, a technical report, an
  arXiv preprint without a DataCite record). When an entry has only a `url`,
  look for a DOI before accepting it (step 2).
- **Keys are the fidelity keys** (`G02`, `R05`, `DDG04`), so `[G02] §3.2` in
  the sheet, in a code comment and in the bib is one work. A work in
  CONTRIBUTING's "References" key table takes the table's key in every
  file; where another bib in the repository (AntHocNet's `paper/paper.bib`)
  uses a different key for it, rename it there too. Otherwise reuse the key
  that other bib already uses, or the sheet's when it cites numbers: one key
  per work across every file, and entries both files carry stay identical.
- **Each entry has a role** in `keywords`: `implemented` (what the code
  follows), `restates` (a later description of the same algorithm),
  `compared` (a protocol or result the repository compares against),
  `dataset`, `tool` (software it builds on: ns-3, an org release),
  `background`. The roles decide what reaches `CITATION.cff`
  (`implemented`, `tool`, `dataset`).
- **Never the repository's own DOI**: that is `CITATION.cff`'s own `doi`;
  listing it again makes the repository cite itself.
- **Never the private paper store.** The org keeps paper copies in a private
  repository; a public file never names it, points into it, or says where a
  copy is kept. Say what was read and cite it by its DOI link.
- **A repository that used no paper** still has the file: it lists the org
  releases it builds on (`tool`), or stays empty with the header that says
  so.

## 1. Inventory

```bash
"$T" fidelity bib check .            # the bib against the sheet, the rules above, the private-library text
"$T" fidelity bib check . --online   # also asks Crossref for a DOI for every url-only entry
```

It lists, one line each: keys the sheet cites that the bib lacks, entries no
file cites and that carry no role, entries with neither `doi` nor `url`, a
rendered reference that is not its DOI link, url-only entries Crossref can
match, and every public line that mentions the private library.

Then find what the repository cites outside the sheet, since those are the
references a protocol's bib most often misses:

```bash
git grep -nE 'doi\.org/10\.|\b10\.[0-9]{4,}/' -- ':!*.bib' ':!docs/references.bib'
git grep -nE '\[[A-Z][A-Za-z]*[0-9]{2}[a-z]?\]' -- '*.md' '*.h' '*.cc' '*.py'
```

Check `README.md`, `docs/`, `CITATION.cff`, code comments, test fixtures
(a fixture derived from a published dataset cites the dataset) and the
org releases the repository builds on (a pinned `core/`, a harness, an
image). DOIs under `skills/*/evals/` or test fixtures of a lookup tool are test
inputs, not references; leave them out.

## 2. Confirm each work and write its entry

```bash
"$T" fidelity bib entry DOI --key G02 --role implemented   # a BibTeX entry from Crossref's record
"$T" lit-search confirm DOI                                # Crossref vs Semantic Scholar and OpenAlex, field by field
"$T" lit-search confirm --title "exact title" --year 2007  # a work without a DOI: find one, or confirm it has none
"$T" zenodo bibtex REPO --role tool                        # an org release: its concept record as @software, keyed from CONTRIBUTING's table
```

Paste the printed entry into `docs/references.bib` as it is. Run `confirm`
when `bib entry` or the sheet disagree with each other: a `differ` in year or
pages is settled on the publisher's page (online-first year against issue
year is the usual cause), never by picking the convenient value; say which
you used in the PR. A work that seems to have no DOI may still have a DataCite one
(university repositories, technical reports): look at the repository's own
record page before settling for a `url`. A work that has no DOI gets a `url`
to the institution's or publisher's page, never to a private copy. If nothing confirms a work, do
not add it: name it in the PR as unconfirmed, and reword every place the
sheet cites its key (`[R05] §3`) to name the work in prose instead, since
`bib check` fails on a cited key the bib lacks. A row whose Source rests on that work
alone gets Source `unknown` (the sheet's check accepts only a `[KEY]`
locator, `repo choice` or `unknown` there) and names the work in its Status.

Two cases need care:

- **A Crossref record that is wrong or thin** (an author missing, diacritics
  dropped, given and family names swapped, words run together, no year): the publisher's page decides. Correct that one field by hand,
  and say in the PR which field, what Crossref had and which page settled
  it. Without the publisher's page, an error two other
  records agree on (`lit-search confirm` prints them) may be corrected from
  them, said in the PR; otherwise keep Crossref's value and say so.
- **A work with no DOI whose title matches another work** (a dissertation
  and the later book chapter with its title): `bib check --online` keeps
  warning that the title has a DOI. Keep the url when the sheet cites the
  work without a DOI (its locators are the dissertation's), and name the
  other work's DOI in the PR so a reviewer sees it was ruled out.

An entry may carry a `note`: one line, in the repository's words, saying
why the work is cited (org-sync renders it as the role line; without it the
role's generic sentence is shown). Neither script writes it; add it after
pasting. Keys are one per work across the org: use the key CONTRIBUTING's
"References" key table gives the work (`zenodo bibtex` fills it in for an
org release); a work not in the table takes its fidelity key. A repository that
cites nothing keeps the seed header and may add a `%` line saying why.

Keep the entries sorted by key. Give each the narrowest true role; when a
work is both followed and compared against, `implemented` wins.

## 3. Regenerate

```bash
"$T" fidelity bib sources .                 # the Sources table in docs/fidelity.md, between its markers
"$T" org-sync apply .                       # the README's citing section
"$T" org-sync reseed CITATION.cff .         # CITATION.cff is a seed: apply never rewrites it
```

A sheet whose Sources table has no `<!-- fidelity:sources:begin -->` /
`<!-- fidelity:sources:end -->` markers gets them around the existing table
(the table is the bib's from then on). `org-sync apply` also rewrites any
other template drift the repository carries; keep only the citing changes
in this PR (`git checkout` the rest) and leave the drift to org-bot's
refresh PR.

The bib takes over `CITATION.cff` and the README's citing list once it holds
an entry; from then on org-sync warns that the repository's `[[references]]`
in `.github/org-sync.toml` is redundant: remove that table in the same PR, so
the bib is the only source. A repository without `citation = true` in its org-sync config keeps its own
README citing section and `CITATION.cff`: org-sync renders neither, so
update only `CITATION.cff`'s `references:` (the org's references tooling
writes that block alone; see CONTRIBUTING "References") and leave the rest.
A repository with no `.github/org-sync.toml` is not on the templates yet:
do not run `org-sync init` for this task; say that `CITATION.cff` and the
README were not regenerated and that `org_sync.py apply` is the remaining step.
Never edit a generated section by hand: the next run undoes it. If a fidelity
row's prose names a work the bib does not hold, add the entry; if a source is
no longer cited, drop its entry or give it a role that explains why it stays.
Reword every private-store line the check printed, then grep for what the
check cannot see: paths into the store (a `$PAPERS/...` variable, a
`<repo>/library/...` path, a home-directory default) and words for it
("papers repo", "the library"); reword those too.

## 4. Verify and hand over

```bash
"$T" fidelity bib check . --online   # clean
"$T" org-sync check .                # no drift
```

Open the PR with a `docs:` title (`docs: docs/references.bib holds the
protocol's sources`), `Part of` the repository's ticket while a box stays
open, and in the body: the entries added (key, role, DOI link), any `differ`
and how it was settled, works left unconfirmed, and the private-library lines
reworded.

## Reporting without changing anything

Asked only which papers a repository follows, or how to cite it: run step 1,
read `docs/references.bib`, and answer with the DOI links and roles. Name
anything the check printed, but make no change.
