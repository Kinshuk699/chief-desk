# Card body template

Workers see ONLY their card (plus parent handoffs and comments). Write the body so a
capable stranger could do the work with nothing else.

```markdown
## Context
<why this card exists; one paragraph of the project goal>

## Your task
<the specific slice: verbs, scope, what is out of scope>

## Decisions already made (don't reopen)
- <copied verbatim from the Work Order>

## Inputs
- <absolute paths, URLs, parent card outputs to read>

## Output
- File: <exact relative path inside the project folder>
- Format: <structure, e.g. claims ledger table: claim | URL | published date | quote>

## Acceptance criteria
- [ ] <checkable>
- [ ] <checkable>

## Constraints
- As-of date: <YYYY-MM-DD>; sources older than <window> flagged STALE unless timeless
- <budget/time/scope limits>
```

## Standard lines for research projects (paste into the right cards)

Researcher cards, under "Decisions already made":
```markdown
- Key claims (premise, money, scale, dates, legal/procurement rules) need TWO independent sources:
  different publishers, and the second must not just repeat the first (stories quoting one government
  release count as one source; cite the primary). If you can't find a second, mark the row SINGLE-SOURCE.
- Tables with old-vs-new columns (e.g. DPP 2016 vs DAP 2020): quote the column you use and name it.
- Primary-source target: every key claim has a primary source or a NO PRIMARY FOUND row listing where
  you looked; at least 60% of all your sources are primary. Below that, dig deeper before handing off
  (your soul says where and how). Tag each row PRIMARY / NEWS / VENDOR / SECONDARY.
- If you use grounded-citations' sources.py, first `export HERMES_CITATION_LEDGER=<project>/.citations-<card-key>.json`
  (parallel cards otherwise write into one shared ledger).
- Images from Wikimedia Commons: its API rate-limits parallel searches (HTTP 429); query titles in
  batches of ~5 and pause on 429.
- Foreign-government claims (e.g. PLA): cite the official English site (eng.mod.gov.cn,
  eng.chinamil.com.cn) over tabloid translations, and check the original term (微压氧舱 = "micro-pressure
  oxygen cabin" was flattened to "pressurized oxygen chambers").
- India figures: check the newest annual PIB review for that ministry (e.g. MoD Year End Review, Dec)
  against any news number; it caught 55 vs 53 of 57.
- A lead already listed in your card (e.g. a parliamentary report) gets chased first, not last.
- Standards: check current status (withdrawn? "expires after" clause?) before citing one as in force;
  ISO 10083, ISO 80601-2-69:2020 and the WHO 2020 PSA spec all turned out withdrawn/expired.
- Paywalled standard: cite the free official registry for its identity/status and tag the table values
  SECONDARY (from whoever reproduces them).
- Images: write your own index file `<prefix>-images-<card-key>.md` (parallel cards appending to one
  file collide). Describe an image only from its source page; Chief looks at every image.
```

Writer card, under "Decisions already made":
```markdown
- NOT FOUND rows are findings, not gaps to hide: state them as "no public source found" (absence of
  evidence, not evidence of absence), especially in a premise check.
- SINGLE-SOURCE key claims are allowed but say "one source" in the sentence.
```

Skeptic card, under "Your task":
```markdown
- For every key claim, check the two sources really are independent (different publisher, not one
  citing the other). One real source = SINGLE-SOURCE, not SUPPORTED-twice.
- Re-read any number taken from a multi-column table against the column header.
- Report the primary-source share per ledger and list key claims with no primary source.
- Any date that limits something ("valid until", "extended to"): is it still in force on the as-of date?
  "In force till <date> or till reviewed" stays in force until a replacement is promulgated (look for
  one; a draft doesn't count). "Extended until <date>" with the date passed = expired unless you find a
  later extension. (v2 shelters: skeptic called DAP 2020 stale and missed an expired emergency route.)
- Your per-row verdict table gets a column `my check` whose only allowed values are `JEV <conf>`,
  `OWN: "<line you saw yourself>"`, or `UNCHECKED (<why>)`. "Verified by w1/parent/researcher" is not a
  value: the rule below was ignored twice when it was only prose (28 rows in the run after it was added).
  Jev's blind spots need your own fetch, not a pass: Chinese/CJK PDFs, paywalled journals (403), and
  numbers inside multi-column code tables. Fetch the text yourself (curl + pymupdf, or the publisher's
  free abstract/registry), grep for the number, paste the line; else UNCHECKED. Report the count of
  UNCHECKED key claims in your summary line.
- Output a counted `parent_verified:` list (row ids you passed without your own or Jev's fetch). Any row
  whose note says "parent confirms" / "researcher confirms" or whose `my check` is UNCHECKED but verdict
  SUPPORTED belongs on this list; it is not 0 if such rows exist. Chief re-checks every
  key row on it before writing; the rule alone didn't stop it (v3: 150 rows, v4: 28 rows; causes: scanned PDFs, CJK,
  publisher 403s, multi-column tables).
- Never accept "parent-verified" for a key claim: if your fetch fails, use the route in
  ACCESS_ROUTES.md (Parliament e-library items need `gov_sources.py sansad-text <uuid> --grep`; the item
  pages are a JavaScript app that fetch tools and jev-judge see as empty). Still blocked = UNCHECKED.
  "PDF fetched by researcher, quote verified at research time" IS parent-verified: jev-judge now reads
  PDFs and Parliament items itself, so a QUOTE_NOT_FOUND on a fetched PDF is a real mismatch (reworded
  or wrong): hand-check it or mark WEAK. (v3: 150 of 243 rows had been passed this way.)
- A primary site that won't load (e.g. idex.gov.in, dgqadefence.gov.in failed from this Mac on
  2026-10-23): try the blocked-page-recovery skill (archived copies) before marking UNCHECKED.
```

Expert-benchmark card (assignee researcher, `parents=[all research cards]`, runs beside the skeptic):
```markdown
## Your task
Find the 1-3 best existing expert analyses of this exact question (think-tank papers, academic
reviews, parliamentary or government reports, serious industry analysts; newest first). For each:
title, author/org, date, URL. Then compare them with our ledgers (in your parent results):
1. What they cover that our ledgers miss (each with their source).
2. Where they disagree with a ledger row (row number, their claim, their source).
3. Good sources they cite that we didn't use.
## Output
`BENCHMARK.md`: the reports list, then sections 1-3 as tables. No benchmark found after a real search =
say so with the searches you ran; that's a valid answer.
```

## Tool call shape

```
kanban_create(
  board="desk",
  title="research: <slice>",
  assignee="researcher",
  body=<template above>,
  parents=[...],                       # fan-in
  skills=["grounded-citations"],       # optional: only for prose outputs with a Sources block; table
                                       # ledgers don't need it (worker feedback, 3 runs in a row)
  workspace_kind="dir",
  workspace_path="/Users/Kinshuk/ChiefDesk/projects/<slug>",
  max_runtime_seconds=3600,            # optional guard
  # model="deepseek-v4-flash",          # optional cheaper/stronger override
  # goal_mode=True, goal_max_turns=12,  # open-ended + crisp acceptance only
)
```

CLI equivalent (old sessions without the kanban toolset):
`hermes kanban --board desk create "<title>" --assignee researcher --body "$(cat card.md)" --workspace dir:/Users/Kinshuk/ChiefDesk/projects/<slug> [--parent <id>] [--skill <name>] [--goal]`
