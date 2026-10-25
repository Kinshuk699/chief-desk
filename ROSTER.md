# Roster: general desk

Chief routes ONLY to profiles listed in "Active". Update this file whenever a profile is
minted, changed or retired. Models: verify with `hermes profile list`.

## Active

| Profile | Soul in one line | Model | Use for | Don't use for |
|---|---|---|---|---|
| researcher | Training data is stale; every claim gets URL + date + quote | deepseek-v4-pro | Finding and citing: topics, companies, people (public sources), current state of X, prior art, docs | Synthesis, opinions, writing for an audience |
| skeptic | Adversarial checker; false PASS is the worst sin | glm-4.7 (zai), different family; ~$5 credit pool | Verifying ledgers/syntheses/drafts, currency checks, AI-tell scans, final gate before Chief. Runs `jev-judge` claims mode first on every ledger | Doing research, fixing work |
| maker | Pragmatic engineer; runs it before claiming done | deepseek-v4-pro | Code, tools, apps, automations (dry-run + human approval), data work, documents/files, reverse engineering with REA | Prose in Kinshuk's voice |
| writer | Disappears into a voice; never invents facts | deepseek-v4-pro | Articles, applications, cover letters, scripts, humanizing drafts, editing. Runs `jev-judge` prose mode before every handoff | Facts not in its inputs; final user-facing polish when it really matters (Chief does that pass) |

Fallback: if nothing fits and the minting test fails, Chief does the card itself or splits it differently.

## Never assign (NSE stock desk, separate system with its own board)
builder · designer · fund-analyst · guardian · orchestrator · scout · tech-analyst · verifier

## Candidates (mint only when a real task needs one AND the minting test passes)
| Candidate | Likely trigger | Minting reason it would satisfy |
|---|---|---|
| coach | Interview prep / tutoring that recurs | Own memory of Kinshuk's stories across sessions; Socratic temperament conflicts with writer |
| ui-designer | Visual work beyond what maker does well | Taste + render-and-compare temperament; possibly a vision-strong model |
| reverser | Clone work becomes repeated | Evidence-first posture; could run in a sandboxed terminal backend |
| playtester | First game/app/site build | Adversarial-user temperament (maker wants to ship, playtester wants to break it); browser + vision posture; every build needs one |

## Mint log
| Date | Profile | Why | Status |
|---|---|---|---|
| 2026-10-22 | researcher, skeptic, maker, writer | Initial general roster | active |
