# ChiefDesk

A multi-profile research and build desk for [Hermes Agent](https://hermes-agent.nousresearch.com/docs).
**Chief** (the default profile, a strong model) plans, routes and verifies; four cheap **worker profiles**
do the bulk work on a kanban board called `desk`. Every run ends with a learning step.

```
Kinshuk ──► Chief (Opus) ──plans──► WORK_ORDER.md
               │  cards on board "desk"
     ┌─────────┼──────────┬──────────┐
 researcher  researcher  maker     writer      (DeepSeek, parallel)
     └─────────┴────┬─────┴──────────┘
                 skeptic (GLM-4.7, different model family) + jev-judge first pass
                    │
               Chief: live re-checks of key claims, sizing maths, writing, PDF, page check
                    │
               Step 8 Learn: SCOREBOARD.md row, RETRO.md, skill/template patches
```

## What's here
| Path | What |
|---|---|
| `skills/chief-desk/` | Chief's procedure: routing, card template, quality rules, precedents |
| `skills/jev-judge/` | Cheap claim/prose pre-sorting with TypeSafe's Jev (script + calibration) |
| `skills/kinshuk-context/` | Facts about Kinshuk and his writing voice |
| `profiles/<worker>/` | Each worker's `SOUL.md` (personality/rules) and `config.yaml` (model) |
| `ROSTER.md` | Which profiles exist and what each is for |
| `.hermes.md` | Rules every worker inherits (handoff format, required `lessons`) |
| `SCOREBOARD.md` | One row per run: time, cost, errors, what changed (the self-improvement log) |
| `ACCESS_ROUTES.md` | How to reach sources that "won't load" (gov.in, Parliament e-library, Wayback) |
| `tools/` | `gov_sources.py` (Parliament/Wayback/Crossref helper), `firecrawl_credits.py` (credit check + key switch) |
| `bin/` | `install.sh`, `mint-profile.sh` (new worker), `sync-from-hermes.sh` (refresh this repo) |

## Use it
- **On this Mac, in any new Hermes chat** (default profile): "use the chief-desk skill" and give the task.
  Skills, profiles and the board already live in `~/.hermes`.
- **On another machine:** install Hermes, put `DEEPSEEK_API_KEY`, `GLM_API_KEY`, `FIRECRAWL_API_KEY`,
  `TYPESAFE_API_KEY` in `~/.hermes/.env`, then `git clone` this repo and run `bin/install.sh`.
- **After the desk learns something:** `bin/sync-from-hermes.sh`, then commit and push.

Never committed: API keys, `.env` files, sessions, memories, and the research projects (`projects/`).
