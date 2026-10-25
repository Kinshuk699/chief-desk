# Jev (TypeSafe AI): what it is for, where it fits, status

**What it is** (verified 2026-10-22/23 from typesafe.ai, docs.typesafe.ai, langchain.com):
TypeSafe's first "System One" model, released 2026-09-15 in early access. It does not
generate text. You send `state` plus typed `questions` (noul = probability of yes; choice
<= 255 options; score 2-10 ordered levels) and get probabilities back in ~0.3 s. Input
$0.042 per M tokens, output free. Limits: 64K tokens/request, 32K/question. SDKs exist
(`typesafe-sdk`, `langchain-typesafe`) but `jev-judge` uses plain HTTP. Integration facts
(endpoint, schema, data terms): `~/ChiefDesk/projects/2026-10-22-jev-integration-facts/SYNTHESIS.md`.
TypeSafe's own agent skill: raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md.

**Status: BUILT and wired (2026-10-23).** Skill `jev-judge`
(`autonomous-ai-agents/jev-judge`): `scripts/jev_check.py` (claims / prose / raw / models,
stdlib only, pinned `jev-1.14.0`), calibrated on 20 claim pairs + 12 paragraphs
(`references/calibration.md`: 19/20, zero false SUPPORTED, AUTO gate 0.80). Wired into the
skeptic and writer SOUL.md files; both smoke-tested end to end from their own souls.
Key in `~/.hermes/.env` and the four worker `.env` files. Kinshuk keeps this key (no rotation,
decided 2026-10-23) and topped up about $2 that day; at ~$0.002 per 50-row ledger that lasts.

## What it is actually used for (outside the desk)
- **Vendor's framing** (blog, 2026-09-15): "smart if-statements" inside software: classify,
  route, score, extract, branch; map-reduce over big datasets; real-time apps; and "verify
  everything": score, judge, verify, guardrail, detect jailbreaks of LLM outputs.
- **LangChain** (blog, 2026-09-17): model-routing middleware (pick a cheap or strong model per
  request) and Auto Mode (classify a tool call as dangerous before it runs). Their summary:
  LLM for open-ended reasoning and generation, Jev for fast structured decisions along the way.
- **Production case** (vendor-published, 2026-10-07): Jack & Jill replaced Gemini Flash Lite in
  the first screening stage (6,000 candidates per role down to a 2,000 shortlist): same recall,
  88% cheaper, about 2x faster, then spread to 15+ workflows.
- **Docs cookbook "citation check"**: string-match the quote, then one Choice
  (supports / contradicts / says_nothing) with a 0.8 confidence gate. `jev-judge` claims mode
  is built on this.

## Can it serve every decision point? No, only some
A decision point is Jev-shaped only when ALL hold:
1. The answer is a closed set fixed in advance (yes/no, pick one, rate on a scale).
2. Everything needed is in the state you send. Jev can't browse, call tools, read files or ask.
3. Nobody needs the reasoning: it returns numbers, no explanation.
4. Occasional error is caught downstream (it is probabilistic and not deterministic:
   low-confidence answers drifted up to 0.21 between identical runs).
5. The data may go to a US third party.
Rule of thumb: you would run it 50+ times and a calibrated probability is enough -> Jev. You
would want a paragraph explaining why, or it happens once and matters a lot -> Chief or an LLM.

| Desk decision point | Jev? | Why |
|---|---|---|
| Claim supported by its quoted source (skeptic) | **Yes, built** | Closed answer, passage in hand, high volume |
| AI tells per paragraph (writer) | **Yes, built** | Closed answer per tell, high volume |
| Inside maker builds: dedupe/entity match, field validation, routing, job fit, next action among N elements | **Yes, best fit** | Per-item loops (the flight-booking pattern). Maker defaults to Jev over an LLM call per item |
| Acceptance criterion met; scoring changes to v1 per criterion (Build rule) | **Partly** | Text-checkable criteria yes; "does it run / is it fast" no: run it |
| Worker blocked: would the answer change direction? | **Advisory** | A noul can suggest; Chief decides |
| Accept a worker's deliverable | **Pre-filter only** | Chief's live spot-check rule stands |
| Tier, shape, Work Order, card assignment | No | Needs the conversation, `clarify`, and judgment; one-off and high-leverage |
| Mint a profile, second build justified | No | Multi-factor, needs a written reason; second build is a human gate |
| Source legality | No | Needs research and written reasoning; legal stakes |
| STALE / true-as-of-today | No | Jev never sees the date or fetches anything |
| Code correctness | No | Run the tests |
| Hermes `goal_judge` aux slot | No | Expects a text verdict and reason |

## Wiring rules
- Everything sent is public text or drafts meant for publication; nothing private.
- Jev output is a signal, never an action trigger (`state` holds untrusted page text).
- A new question means a new calibration (~20 known answers) before trusting its threshold.
