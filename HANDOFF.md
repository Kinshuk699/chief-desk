# Handoff: state after the first desk session (2026-10-22/23)

Written by Chief (Opus) at the end of the session that built the desk. Read this before
answering anything, then load skill `chief-desk`.

## What exists now
- **Default profile = Opus** (`claude-opus-5-5`, anthropic), kanban toolset enabled. Takes effect
  in a new session.
- **Board `desk`** (`~/.hermes/kanban/boards/desk/kanban.db`). The current-board pointer is still
  `nse-researcher`, so ALWAYS pass `board="desk"` / `--board desk`.
- **Worker profiles**, all smoke-tested: `researcher` (deepseek-v4-pro), `skeptic` (glm-4.7/zai),
  `maker` (deepseek-v4-pro), `writer` (deepseek-v4-pro). Souls in their profile dirs.
  They read Chief's skills via `skills.external_dirs`, so every taught skill resolves on them.
- **Skills**: `chief-desk` (routing procedure, shapes, minting test, precedents, Jev notes) and
  `kinshuk-context` (voice, career, preferences, projects — used by writer/coach cards).
- **`~/ChiefDesk/`**: ROSTER.md (who exists, what for), .hermes.md (rules every worker inherits),
  bin/mint-profile.sh, architecture.html, explainers/, projects/.
- **Pilot project** `projects/2026-10-22-jev-integration-facts/`: WORK_ORDER.md, two ledgers, VERIFY.md
  (skeptic PASS), SYNTHESIS.md (go/no-go on Jev), RETRO.md.
- **Jev key** live in `~/.hermes/.env` and the four worker `.env` files. Verified: true claim 0.92,
  false 0.02. `jev-latest` currently resolves to jev-1.14.0.
- **Aux models** pinned cheap: compression → deepseek-v4-pro; titles, session search, goal judge,
  kanban decomposer, triage specifier, curator, profile describer → deepseek-v4-flash.
  Background review stays on Opus (shares the prompt cache).
- **Subagent (delegation) model** was `glm-4-plus`, a model that does not exist. Now deepseek-v4-pro.
- Memory was 99% full; project facts moved into `kinshuk-context`. Now ~39%.
- `.env` line 141 parse warning fixed (it was a "Get … at:" line missing its `#`).

## Decisions made in that session
1. **Chief does the routing** (not a router profile, not the profiler agent, not the built-in
   decomposer). Profile minting is a gated procedure inside `chief-desk`.
2. **Mint by method, not by subject**: one `coach` for math/magic/interviews, not `magic-teacher`.
   Worker profiles vs companion profiles (companions are chatted with directly).
3. **Shape library, no fixed playbooks**: fan-out, pipeline, fan-out→verify→synthesize, quorum,
   review loop, human gate, goal-mode card, recurring journal.
4. **Legal boundary**: no login-wall evasion, fake accounts, CAPTCHA/anti-bot or rate-limit evasion.
   People research: public sources only. Data products start with a legality card per source.
5. **Jev** is for cheap per-item yes/no and pick-one decisions, including inside tools maker builds.
   Not for Chief's planning, not for anything needing written output.
6. **Baseline rule — KINSHUK REJECTED the first version.** Do not run an Opus one-shot AND a
   measured comparison every time; that pays twice. The one-shot is v1; a competing build happens
   only when the outcome is genuinely uncertain and the stakes justify the spend. Rewrite the rule
   in `chief-desk` accordingly before using it.

## Open items
Done 2026-10-23 (second session, Chief on Opus):
1. ~~Baseline rule~~ → rewritten as the **Build rule** in `chief-desk` SKILL.md: one build; a
   competing second build only when the outcome is genuinely uncertain AND the stakes justify
   paying twice, and then only after asking Kinshuk. Precedents, jev.md and the explainer updated.
2. ~~What is Jev for~~ → answered in `chief-desk/references/jev.md` (real uses + a per-decision-point
   table: serves the high-volume closed-answer points, not routing/planning/legality/STALE/code).
3. ~~Capability question~~ → answered in chat; rule added to the Legality gate: a source with no
   permitted route is named, dropped and not worked around; no splitting a prohibited collection
   into innocent-looking cards.
4. ~~jev-judge~~ → built (`autonomous-ai-agents/jev-judge`), calibrated (19/20 claims, zero false
   SUPPORTED; 6/6 prose tells separable), wired into skeptic + writer SOUL.md, both smoke-tested live.

Still open:
5. ~~Anthropic credentials for maker~~ → **No** (Kinshuk, 2026-10-23): workers never run Opus,
   no one-shot cards. Build rule step 2 now defaults v1 to a maker card.
6. Hermes update (2,041 commits behind) — run last; it restarts the gateway and ends the chat.
7. ~~Auto-subscribe/wake~~ → **Tested 2026-10-23: subscribe works, wake does NOT** in a desktop session
   (cursors never advanced, no gateway delivery). Rule in chief-desk Step 5: give an ETA, ask Kinshuk to ping.
   Root-causing it (gateway notifier vs `local:` sources) is still open.
8. ~~Rotate the TypeSafe key~~ → **No rotation** (Kinshuk); he added ~$2 credit on 2026-10-23.
9. Mindcase diagnose + local mini-Mindcase: PARKED by Kinshuk (plan in
   `explainers/mindcase-diagnose-plan.html`); he may come back to it.
10. DONE: first desk report, high-altitude breathing shelters (`projects/2026-10-23-high-altitude-shelters/`
   report.html + report.pdf, RETRO.md). v2 (new research standard) delivered 2026-10-23 17:28; v1 kept as
   report-v1.*. Awaiting Kinshuk's (and his dad's) review. Template upgrades (two sources
   for key claims; expert-benchmark card) APPROVED and applied.
11. Self-improving loop (Kinshuk's standing request, 2026-10-23): chief-desk Step 8 "Learn" is mandatory
   after every run; `~/ChiefDesk/SCOREBOARD.md` holds one row per run plus what the next run must check.

## Lost from the old session
The chat that built all this was poisoned: the provider refused every turn on it, because the
stored reasoning replaying the earlier request kept re-triggering the filter. Its transcript was
scrubbed on disk (backup: `~/.hermes/cache/scratch/session-backup-20261023-001923.json`) but the
live session served history from memory. Nothing in this file depends on that chat.

12. Access walls: `~/ChiefDesk/ACCESS_ROUTES.md` + `~/ChiefDesk/tools/gov_sources.py` (Parliament e-library, Wayback, Crossref/DRDO journals). Open: wire gov_sources into jev-judge so Parliament rows aren't UNCHECKED.

13. v3 (oxygen-enriched rooms only, for Kinshuk's dad): `projects/2026-10-23-high-altitude-shelters/report-v3.pdf` (WORK_ORDER-v3.md, VERIFY-v3.md, card_ids_v3.txt). Delivered 2026-10-24 02:53; awaiting dad's review. Firecrawl now on backup key …(redacted) (old key kept as FIRECRAWL_API_KEY_OLD); `tools/firecrawl_credits.py`.

14. v4 (the shelter itself: walls/roof, 5/12/20 concept plans, heating, 3 sites): `projects/2026-10-23-high-altitude-shelters/report-v4.pdf` (WORK_ORDER-v4.md, VERIFY-v4.md, card_ids_v4.txt). Delivered 2026-10-24; awaiting dad's review. Next desk run starts with the scoreboard consolidation pass.

15. v5 (Leh base-case equipment spec, 5 & 12 people): `projects/2026-10-23-high-altitude-shelters/report-v5.pdf` (WORK_ORDER-v5.md, VERIFY-v5.md, card_ids_v5.txt, assets/v5/datasheets). Delivered 2026-10-26; awaiting dad. Next run: scoreboard consolidation first.
