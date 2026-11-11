---
name: lit-search
description: "Find new or newer papers on a topic and confirm references, from free sources only (Crossref, Semantic Scholar, OpenCitations, arXiv, OpenAlex single-record lookups; no paid service, no key needed). Use whenever someone asks for follow-up work or what cites a paper, a paper's references, related work, a literature search for a review, a survey or a fidelity sheet, papers on a protocol family or network type since some year, or whether a reference (DOI, year, venue, pages, authors) is right, including a thesis or report without a DOI. Script first: lit_search.py prints one line per work from the sources' records; never write a citation field, DOI or result from memory."
license: MIT OR GPL-2.0-only
compatibility: Needs git, python3 and network access to github.com (scripts/lit-search clones swarm-routing/.github tools/lit-search) and to api.crossref.org, api.semanticscholar.org, api.opencitations.net, export.arxiv.org and api.openalex.org.
metadata:
  author: swarm-routing
  repository: https://github.com/swarm-routing/skills
---

# lit-search

A literature search written from memory invents papers, years and venues. This
skill finds candidates through public scholarly indexes and confirms each one
against its registry record, so every paper you report can be traced to a
record.

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/lit-search"   # as the Claude Code plugin
# installed with skills.sh (npx skills add): SKILL=<the directory this SKILL.md is in>
LS="$SKILL/scripts/lit-search"
"$LS" citing DOI [--since 2023] [--sort cited|year] [--limit 10]   # who cites it
"$LS" refs DOI                                                     # what it cites
"$LS" search "few precise words" [--since Y] [--until Y] [--type article] [--crossref] [--preprints]
"$LS" related DOI                                                  # last resort, noisy
"$LS" confirm DOI                                                  # one reference, field by field
"$LS" confirm --title "exact title" [--year Y]                     # a work without a DOI
```

Inside a `swarm-routing/.github` checkout, `python3 -I
tools/lit-search/lit_search.py …` is the same; `ORG_TOOLS_DIR=<checkout>`
points the wrapper at a local one. After any command, `--library FILE …`
marks the works whose DOIs those Markdown files name (`[saved]`, or
`[listed]` for a file whose name contains "download"); `--abstract` adds a
60-word abstract.

**Every source is free.** Crossref, Semantic Scholar, OpenCitations, arXiv
and OpenAlex's single-record lookups need no key and cost nothing. No paid
service is needed. Two optional free keys only lift limits, never unlock
anything the procedure depends on: `S2_API_KEY` (Semantic Scholar's shared
keyless pool answers HTTP 429 when busy) and `OPENALEX_API_KEY` (enables
`search --openalex`; OpenAlex searches draw on a daily budget). Never ask for,
create or paste a key; never send an email address anywhere.

## 1. Discover, in this order

Each line is `year · title · venue · DOI · cited N · open access · source`.
Calls are few and cached (lists 1 day, records 30 days); run commands one
after another, not in parallel.

1. **`citing` a known seed paper** (OpenCitations, then one Semantic Scholar
   batch for titles). The best route to newer work: sorted by citations,
   `--since` for recent follow-ups, `--sort year` for the newest. Venue and
   count on each line make weak sources stand out.
2. **`refs` of the seed or of a strong citer**: the older work it builds on.
3. **A narrow `search`**: a few precise words, a year range and a type; one
   or two searches, not a sweep. `--crossref` and `--preprints` (arXiv) widen
   it; each source's list is labelled.
4. **`related` only if the above found nothing.** Semantic Scholar's
   recommendations are noisy and recency-biased (many undated, uncited or
   off-topic entries); a last resort.

Seed DOIs come from a record (`confirm`, the library, the paper itself),
never from memory. Exit 3 means a source is rate-limited: what was printed
stands; try later or narrow the query, do not loop.

## 2. Screen

Read titles (and `--abstract` when a title is unclear). Keep a paper only
when you can say what it adds to the task at hand (an issue, a review row, a
parameter). Drop off-topic citers (a routing paper cited by an option-pricing
paper is common) and say how many you dropped. A venue you cannot place, no
DOI and no citations together are a warning sign, not a disqualification:
note it.

## 3. Confirm every paper you keep

```bash
"$LS" confirm DOI
```

prints Crossref's record beside Semantic Scholar's and OpenAlex's, a verdict
per field, and exits 1 on a `differ` in year, venue, authors or pages. Write
citations from Crossref's fields. A `differ` is resolved on the publisher's
page (an online-first year against the issue year is the usual cause), never
by picking the convenient value; say which you used. `unavailable` means a
cross-check source was down: the Crossref fields still stand, say it was not
cross-checked. When Crossref has no record (a DataCite DOI, such as arXiv's
`10.48550/…`), cite from a source that has one and name it ("fields from
Semantic Scholar"), or mark the citation unconfirmed; never fill the gap from
memory.

A work without a DOI (a thesis, a tech report): `confirm --title` shows the
best matches of Crossref and Semantic Scholar, each labelled. A match whose
title differs is another work (often the journal version); the work itself
is confirmed on its institution's or publisher's page (a repository handle,
the report series), and the report says the record is not in a registry.

## 4. Hand over or report

- **With the private library the maintainer keeps checked out**: hand
  each kept paper to its `lit-source` skill, which verifies the citation,
  finds legitimate open copies and files it; pass `--library` with that
  library's README.md and MANUAL-DOWNLOADS.md so the lines say what is
  already there. Nothing is added to the library without the maintainer's
  go-ahead, unless the task says so.
- **Otherwise** report the candidates as a table:

  | Paper (Crossref fields) | DOI | Cited | Why it matters (which issue) | Status |
  |---|---|---|---|---|

  with the DOI and fields from `confirm`, never from a search line alone, and
  the searches you ran (command, date) so the search can be repeated.
- **In a public issue, PR or doc**, cite each paper by its
  `https://doi.org/<DOI>` link (the maintainer's preference), or, without a
  DOI, by its publisher's or institution's page; never by a path in, or a
  mention of, the private library.

Only legitimate routes to a paper: the publisher's open access, an author's
or institution's repository, arXiv. Never a shadow library, never a mirror of
a paywalled paper. Nothing from the private papers library (files, extracted
text, paths) goes into a public repository, issue or PR.
