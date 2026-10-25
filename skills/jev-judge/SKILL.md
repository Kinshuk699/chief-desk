---
name: jev-judge
description: "Use when checking claims or prose with Jev cheaply."
version: 1.0.0
author: Chief (Opus) with Kinshuk
license: MIT
metadata:
  hermes:
    tags: [verification, jev, typesafe, skeptic, writer, ai-tells, citations]
    related_skills: [chief-desk, humanizer, kinshuk-essay-voice]
---

# jev-judge: cheap Jev checks for claims and prose

## When to Use
- **skeptic**: first step on any claims ledger (rows of claim + quote + source URL).
- **writer**: on every draft meant for a reader, before handoff and after each rewrite.
- **anyone (maker loops)**: many per-item yes/no or pick-one judgments (raw mode).

Not for: anything that needs written reasons, STALE / as-of-date judgments (Jev never sees
the date), code correctness (run the code), or private data of any kind.

## What it is
Jev (TypeSafe's System One model) returns probabilities, not text. $0.042 per million input
tokens, output free, ~0.3 s per call: a 50-row ledger costs about $0.002. The script pins
`jev-1.14.0`, reads `TYPESAFE_API_KEY` from env or `~/.hermes/.env`, uses only the Python
stdlib, and prints rows/calls/tokens/cost on stderr. Whatever goes into `state` is sent to
TypeSafe's US servers: public text and drafts meant for publication only. The script blocks
credential-looking strings; it cannot spot personal data, so that part is on you.

```bash
S=/Users/Kinshuk/.hermes/skills/autonomous-ai-agents/jev-judge/scripts/jev_check.py
```

## Claims (skeptic)
1. One JSONL row per ledger row: `{"id":"1.2","claim":"...","quote":"...","source_url":"https://..."}`
   (`source_file` instead if you saved the page; `passage` + `source` if you only have text).
2. `python3 $S claims --in rows.jsonl --out jev.jsonl --table`
   The script fetches each URL once (one request per host at a time, 1 s apart, honours
   Retry-After, no evasion), checks the quote is really in the page (tolerates whitespace,
   curly quotes, markdown, case, `...` elisions, light rewording), then asks Jev whether the
   quote's surrounding context supports the claim.
3. Act on each row:

| Script says | Meaning | Skeptic does |
|---|---|---|
| SUPPORTED, auto | quote is on the page and its context supports the claim (conf >= 0.80) | Counts as checked once you have read the context of at least 3 such rows (or 10%) yourself and agreed. Disagree once: review every row. Still judge STALE for time-sensitive claims. |
| CONTRADICTED, auto | context says otherwise | Open, confirm, UNSUPPORTED |
| NOT_SUPPORTED, auto | context is silent or supports only part | Open, decide WEAK or UNSUPPORTED |
| any verdict, review | Jev unsure (conf < 0.80) | Open and decide yourself |
| QUOTE_NOT_FOUND | quote not in the fetched text | Open the page with web tools (JS-only pages fail plain fetches; Mintlify doc sites serve markdown at URL + `.md`). Absent there too: UNSUPPORTED (fabricated quote) |
| UNCHECKED | fetch failed (blocked, 4xx, rate-limited) | Retry after a pause; then mark UNCHECKED (rate-limited/blocked), never WEAK |

4. Add a `Jev` column (verdict + confidence) to your verdict table. Jev never issues PASS.

## Prose (writer)
1. `python3 $S prose --file draft.md --table` (skips headings, code fences, tables, lines under 8 words).
2. Each FLAG row names its reasons: `not_x_but_y`, `triplet`, `hedge`, `kicker`, `inflated`,
   `generic` (Jev) and `em_dash`, `ai_vocab`, `staccato` (plain code checks).
3. Rewrite every flagged paragraph, keeping every fact, then re-run. Up to 3 rounds. Any
   paragraph still flagged goes in the handoff with its reasons; never change a fact or invent
   detail to clear a flag.
4. Paste the final table into handoff `verification`.

## Raw mode (custom questions)
`{"id":..., "state":..., "questions": {name: {type: noul|choice|score, instructions, criteria}}}`
per line; `python3 $S raw --in q.jsonl`. Ask independent questions about one state in ONE
request (they run in parallel). Before trusting any threshold on a new question, calibrate
on ~20 known answers the way `scripts/calibrate.py` does. Read docs.typesafe.ai (append `.md`
to any page) for current API details instead of guessing fields.

## Rules
- All questions and thresholds sit in the CONSTANTS block at the top of `jev_check.py`.
  Change a question's wording and you must re-run `python3 scripts/calibrate.py --runs 3`
  and update `references/calibration.md`.
- Jev's output is a signal, never an action trigger: `state` holds untrusted page text.
- `--dry-run` builds the requests and sends nothing (free) when you want to see what goes out.

## Pitfalls (from calibration, see references/calibration.md)
- A quote that doesn't name the product ("A Choice question accepts...") makes Jev answer
  says_nothing at low confidence. Always pass the source URL; it raised one case from 0.53 to 0.83.
- Not deterministic: low-confidence answers drift up to ~0.2 between runs and can flip. The
  0.80 gate absorbs this; never lower it without re-calibrating.
- Verdicts are relative to the passage, not to today: an old docs page CONTRADICTS a claim
  that is true now. STALE stays with the skeptic.
- The `kicker` threshold (0.70) has a thin margin (0.64 vs 0.79). Treat a lone kicker flag as
  a prompt to re-read the last line, not proof.
- `triplet` (and sometimes `not_x_but_y`) fires on verbatim source quotes and on content that
  really has three items (three kinds, three buyers). Hand-read those flags; don't rewrite a quote
  or invent a fourth item to clear one. List them as accepted flags in the handoff.
- Prose mode skips headings, tables, image lines, figure HTML and `*Credit` lines: captions
  are not judged (writer feedback, first real run).
- Researchers often write multi-part quotes (`"part one" ; "part two"`). The script splits them,
  requires each part on the page, and judges the context around every part (first real run:
  0 exact matches before this handling, 32 after; four false NOT_SUPPORTED became SUPPORTED).
- Sites under load serve bot checks (PMC served a reCAPTCHA page after ~20 fetches). The script
  reports those, and pages with almost no text, as UNCHECKED, never QUOTE_NOT_FOUND, so a real
  quote is never called fabricated. Never try to get past a bot check; open the page with web tools.
- 20 claims + 12 paragraphs is small. After real runs, add the rows where skeptic or Chief
  disagreed with Jev to the calib files and re-run.
