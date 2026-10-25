# Workflow shapes: compose these; don't pick from a fixed menu

| Shape | Graph | Use when | Mechanics |
|---|---|---|---|
| **Single** | 1 card | One role, but needs persistence/audit or a different model | One `kanban_create` |
| **Fan-out** | N siblings, same role | Independent slices (angles, sources, sub-questions, files) | N cards, no parents; slice by non-overlapping scope |
| **Pipeline** | A → B → C | Each stage consumes the previous output | `parents=[prev]`; the parent handoff rides into the child's context |
| **Fan-out → verify → synthesize** | N → (skeptic ∥ benchmark) → writer → Chief | Anything factual that must be right (research, dossiers, company prep) | Skeptic and the expert-benchmark researcher both get `parents=[all N]`; writer gets both as parents |
| **Quorum** | N independent attempts → judge | Judgment calls where variance is the risk (headline, positioning, architecture options) | N cards with the same brief, different temperatures or models; skeptic or Chief picks |
| **Review loop** | maker ⇄ reviewer | Code or artifacts with a quality bar | `kanban_request_review` / `request_changes` on the same card |
| **Human gate** | ... → [Kinshuk] → ... | Direction-changing choice mid-flow (design pick, story choice) | Card blocks `needs_input` with options + recommendation, or Chief pauses and asks |
| **Goal-mode card** | 1 card that loops | Open-ended work with crisp acceptance ("all tests pass", "every page translated") | `goal_mode=true`; body = acceptance criteria |
| **Journal / recurring** | same profile + shared dir + cron | Spaced repetition, monitoring, weekly digests | `cronjob` with a workdir + skills; output to a dir |

## Composition heuristics
- Facts that matter → there is always a skeptic card, and it's a different model family from the producers.
- Prose for Kinshuk → writer draft, skeptic AI-tell + fact scan, then Chief's final voice pass.
- Anything built → maker with tests, then Chief runs it live before reporting.
- Slice fan-outs so outputs don't overlap; tell each slice what the others cover.
- Prefer 3-6 cards. More than 10 means re-slice or split the project.
- A card that would take a worker more than ~2 hours should be split.
