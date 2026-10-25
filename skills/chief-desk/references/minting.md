# Minting a new profile

## The test: mint only if (A or B or C or D) AND E
- **A. Temperament conflict**: the role needs a soul that contradicts an existing one
  (adversarial vs generous, Socratic vs answer-giving, terse vs expansive).
- **B. Model family**: the role must default to a different model family (independence or capability, e.g. vision).
- **C. Tool posture**: different toolsets, sandbox or terminal backend (e.g. no terminal for a pure writer, a sandboxed backend for risky analysis).
- **D. Own memory**: the role should accumulate knowledge across projects (a coach who remembers Kinshuk's interview stories).
- **E. Recurrence**: you can name at least 3 plausible future tasks for it.

If the test fails, specialize cheaper: card body, then `skills=[...]`, then `model=` override.

## Worker vs companion profiles
- **Worker**: driven only by cards; never talks to Kinshuk (researcher, skeptic, maker, writer).
- **Companion**: Kinshuk chats with it directly (Bots pane / `hermes -p <name> chat`) for
  ongoing interaction, e.g. a coach running daily practice. Chief builds the project on the
  board, then hands the live sessions over. State lives in the project folder (PROGRESS.md),
  how-he-learns lives in the companion's memory, subject knowledge lives in a course skill.
- Mint by temperament/method, not by subject: one `coach` for math, magic and interviews; not
  `magic-teacher` (fails recurrence).

## Procedure
1. `~/ChiefDesk/bin/mint-profile.sh <name> <provider> <model> "<one-sentence description>"`
   (blank profile, least-privilege .env, model pinned, cwd ~/ChiefDesk, Chief's skills exposed).
2. Write `~/.hermes/profiles/<name>/SOUL.md` (read the default file first): role identity,
   one professional scar, hard boundaries, handoff shape, under ~1,400 chars. No paths or
   project facts (those go in cards and `.hermes.md`).
3. If C applies: `hermes -p <name> tools disable <toolset>` / set terminal backend.
4. Smoke test: `cd ~/.hermes/cache/scratch && hermes -p <name> chat -q "<one small real task>"`;
   confirm the model in `~/.hermes/profiles/<name>/state.db` sessions.model.
5. Add a row to `~/ChiefDesk/ROSTER.md` (Active + mint log). Tell Kinshuk in the result.

## Retire
Unused for 60 days, or its work keeps getting rerouted: move it to "Retired" in ROSTER.md.
Don't delete the profile without asking Kinshuk.

## Models available (verify live; prices per M tokens in/out)
- deepseek-v4-pro $0.66/$1.98 · deepseek-v4-flash $0.15/$0.60 (1M ctx), the default workers
- glm-4.7 (zai) $0.60/$2.20 (204K ctx), the different family; small credit pool; never glm-5.x for the verifier
- claude-opus-5-5 $4/$20, Chief only; use a card `model=` override only for rare quality-critical cards (needs Anthropic credentials in that profile)
