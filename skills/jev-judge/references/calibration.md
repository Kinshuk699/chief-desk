# Calibration: jev-judge on jev-1.14.0 (2026-10-23)

Known-answer sets live next to the script: `scripts/calib_claims.jsonl` (20 claim/passage
pairs: 8 supports, 7 contradicts, 5 says_nothing) and `scripts/calib_prose.jsonl` (12
paragraphs, each tell labelled present / absent / ambiguous). Passages are real public text
(TypeSafe docs and blog, YouTube, Greenhouse and Reddit API docs, a law-firm blog on hiQ v.
LinkedIn); claims were written to hit specific traps (wrong number, number in the wrong field,
flipped negation, wrong date, half-supported overclaim, unrelated passage from the same vendor).
Re-run any time: `python3 scripts/calibrate.py --runs 3` (about $0.002).

## Decisions taken from the data
| Constant | Value | Why |
|---|---|---|
| `CLAIM_AUTO` | 0.80 | Every wrong answer or run-to-run flip sat at confidence <= 0.51. At 0.80: 17/20 auto, 0 auto-wrong, 3 to review. |
| claim `state.source` | URL of the passage | Run 1 without it: c19 conf 0.53. With it: 0.83-0.91. Skeptic always has the URL. |
| `NOUL_FLAG` (not_x_but_y, triplet, hedge, inflated) | 0.50 | Separable on this set with wide margins (absent max 0.38, present min 0.82). |
| `NOUL_FLAG["kicker"]` | 0.70 | A one-sentence promotional paragraph scored 0.64-0.67 with no kicker; true kickers 0.79+. Thin margin: watch it. |
| `GENERIC_FLAG` | 1.50 | Absent max 0.56, present min 2.87 on the 0..3 scale. |

## Known weaknesses (read before trusting it)
- **Unnamed entity in the passage** (c01: "A Choice question accepts up to 255 options" vs the
  claim "Jev's Choice questions…"): says_nothing at 0.37-0.51 in every run. Low confidence, so
  it goes to review, never auto. Expect this on doc quotes that don't name the product.
- **Not deterministic.** Same request, different runs: confidence drifted up to 0.21 (c07),
  and one low-confidence verdict flipped (c07: supports -> contradicts at 0.20). Flips only
  happened below 0.52, so the 0.80 gate absorbs them.
- **Passage-relative, not true-as-of-today.** c16 ("jev-latest points to 1.14.0") is
  CONTRADICTED by the older docs passage even though it is true today. STALE is the
  skeptic's call; Jev never sees the date.
- 20 + 12 items is a small set. Thresholds are provisional: when skeptic finishes a real
  ledger, compare its final verdicts with the Jev column and re-run calibration with the
  disagreements added as new rows.

## Functional checks (same day, live)
Fetch + locate + judge on real pages: exact quote SUPPORTED (0.95); fabricated quote
QUOTE_NOT_FOUND with no model call; quote with `…` elisions matched; real quote under a wrong
claim CONTRADICTED (0.97); a credential-looking string BLOCKED before sending; prose file split
skipped headings, code fences and tables and flagged the planted paragraph on 6 reasons.

## Raw results, run 2 (3 repeats, with source)

## Claims (choice: supports / contradicts / says_nothing)

| id | label | run1 | conf1 | run2 | run3 | case |
|---|---|---|---|---|---|---|
| c01 | supports | says_nothing ✗ | 0.37 | says_nothing (0.48) | says_nothing (0.51) | limit, exact |
| c02 | contradicts | contradicts | 0.45 | contradicts (0.45) | contradicts (0.4) | wrong number |
| c03 | supports | supports | 0.94 | supports (0.89) | supports (0.97) | negation, paraphrase |
| c04 | contradicts | contradicts | 0.98 | contradicts (0.97) | contradicts (0.98) | negation flipped |
| c05 | supports | supports | 0.91 | supports (0.89) | supports (0.89) | range, paraphrase |
| c06 | says_nothing | says_nothing | 0.98 | says_nothing (0.98) | says_nothing (0.98) | overclaim: half supported |
| c07 | supports | supports | 0.34 | supports (0.41) | contradicts (0.2) | other domain |
| c08 | contradicts | contradicts | 1.0 | contradicts (0.98) | contradicts (1.0) | number moved to wrong field |
| c09 | supports | supports | 0.98 | supports (0.98) | supports (0.98) | other domain |
| c10 | contradicts | contradicts | 0.97 | contradicts (0.97) | contradicts (0.97) | scope flipped |
| c11 | supports | supports | 1.0 | supports (1.0) | supports (0.98) | legal, paraphrase |
| c12 | says_nothing | says_nothing | 0.92 | says_nothing (0.89) | says_nothing (0.89) | overclaim: extra unstated part |
| c13 | supports | supports | 1.0 | supports (1.0) | supports (1.0) | date |
| c14 | contradicts | contradicts | 1.0 | contradicts (1.0) | contradicts (1.0) | wrong date |
| c15 | says_nothing | says_nothing | 1.0 | says_nothing (1.0) | says_nothing (1.0) | same vendor, unrelated passage |
| c16 | contradicts | contradicts | 1.0 | contradicts (1.0) | contradicts (1.0) | version (stale passage; passage-relative label) |
| c17 | says_nothing | says_nothing | 1.0 | says_nothing (0.98) | says_nothing (1.0) | overclaim: half supported |
| c18 | contradicts | contradicts | 1.0 | contradicts (1.0) | contradicts (1.0) | right number, wrong field |
| c19 | supports | supports | 0.83 | supports (0.89) | supports (0.91) | inference across clauses |
| c20 | says_nothing | says_nothing | 1.0 | says_nothing (0.98) | says_nothing (1.0) | overclaim: half supported |

Accuracy (run 1, argmax): 19/20
  supports: 7/8
  contradicts: 7/7
  says_nothing: 5/5
False SUPPORTED (the expensive error): 0 -> []
Wrong answers' confidence: [(0.37, 'c01')]
Right answers' confidence: min 0.34
  AUTO >= 0.6: 17/20 auto, 0 auto-wrong, 3 to review
  AUTO >= 0.7: 17/20 auto, 0 auto-wrong, 3 to review
  AUTO >= 0.8: 17/20 auto, 0 auto-wrong, 3 to review
  AUTO >= 0.9: 16/20 auto, 0 auto-wrong, 4 to review
  AUTO >= 0.95: 13/20 auto, 0 auto-wrong, 7 to review
Stability over 3 runs: 1 verdict flips, max confidence drift 0.140

## Prose (noul p(yes) per tell; generic score 0..3)

| id | not_x_but_y | triplet | hedge | kicker | inflated | generic | code checks |
|---|---|---|---|---|---|---|---|
| p01 | 0.35○ | 0.17○ | 0.04○ | 0.15○ | 0.04○ | 0.11 (low) | em=0 vocab=0 stacc=0 |
| p02 | 0.07○ | 0.09○ | 0.03○ | 0.07○ | 0.02○ | 0.04 (low) | em=0 vocab=0 stacc=0 |
| p03 | 0.97● | 0.34○ | 0.03○ | 0.79● | 0.73 | 2.87 (high) | em=0 vocab=0 stacc=0 |
| p04 | 0.04○ | 0.82● | 0.02○ | 0.50 | 0.34 | 2.91 (high) | em=0 vocab=0 stacc=0 |
| p05 | 0.04○ | 0.33○ | 0.98● | 0.13○ | 0.09○ | 2.96 (high) | em=0 vocab=0 stacc=0 |
| p06 | 0.38○ | 0.24○ | 0.02○ | 0.96● | 0.19○ | 1.00 (None) | em=0 vocab=0 stacc=2 |
| p07 | 0.02○ | 0.18○ | 0.02○ | 0.64○ | 0.98● | 2.98 (high) | em=0 vocab=6 stacc=0 |
| p08 | 0.05○ | 0.15○ | 0.02○ | 0.04○ | 0.04○ | 0.56 (low) | em=0 vocab=0 stacc=0 |
| p09 | 0.96● | 0.92● | 0.02○ | 0.90● | 0.12 | 2.93 (high) | em=0 vocab=0 stacc=0 |
| p10 | 0.18○ | 0.11○ | 0.03○ | 0.06○ | 0.02○ | 0.06 (low) | em=0 vocab=0 stacc=0 |
| p11 | 0.02○ | 0.24○ | 0.02 | 0.24○ | 0.08○ | 2.92 (high) | em=0 vocab=0 stacc=0 |
| p12 | 0.98● | 0.16○ | 0.03○ | 0.12○ | 0.03○ | 0.15 (low) | em=0 vocab=0 stacc=0 |

● = labelled present, ○ = labelled absent, no mark = ambiguous (excluded)
  not_x_but_y: at 0.5: recall 3/3, false flags 0/9; separable: any threshold in (0.38, 0.96]
  triplet: at 0.5: recall 2/2, false flags 0/10; separable: any threshold in (0.34, 0.82]
  hedge: at 0.5: recall 1/1, false flags 0/10; separable: any threshold in (0.04, 0.98]
  kicker: at 0.7: recall 3/3, false flags 0/8; separable: any threshold in (0.64, 0.79]
  inflated: at 0.5: recall 1/1, false flags 0/8; separable: any threshold in (0.19, 0.98]
  generic: at 1.5: recall 6/6, false flags 0/5; separable: any threshold in (0.56, 2.87]
Stability over 3 runs: max noul drift 0.080

96 Jev calls, 54741 input tokens, ~$0.00230, model jev-1.14.0

## First real run (2026-10-23, 84 ledger rows, high-altitude-shelters project)
- With the original matcher: 0 exact quote matches (researchers wrote `"part" ; "part"` quotes), so Jev
  sometimes judged the wrong part of the page. Skeptic overturned 10 of Jev's NOT_SUPPORTED/CONTRADICTED
  verdicts by hand. Jev issued no false SUPPORTED: the safe direction held.
- After the multi-part fix (same rows, non-blocked pages): 32 exact matches, 37 auto-SUPPORTED (was 31),
  4 former false negatives now SUPPORTED (3 checked by eye: correct).
- Lesson: auto NOT_SUPPORTED is a "look here" signal, not a verdict. Only auto SUPPORTED saves skeptic time.
