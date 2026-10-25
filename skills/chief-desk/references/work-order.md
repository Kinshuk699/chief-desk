# Work Order template

Save as `~/ChiefDesk/projects/<YYYY-MM-DD>-<slug>/WORK_ORDER.md`.

```markdown
# <Project title>
Tier: T2 · Board: desk · Folder: ~/ChiefDesk/projects/<slug> · As-of: <YYYY-MM-DD>

## Goal
<one or two sentences: what Kinshuk actually wants and why>

## Deliverable + definition of done
- Deliverable: <file(s)/artifact, format, where>
- Done when: <checkable criteria; how Chief will verify live>

## Assumptions (stated instead of asked)
- ...

## Decisions made once (stamped into every card body)
- Formats / schemas / file names:
- Stack / tools:
- Tone / audience:
- Source rules (recency window, primary-source preference):
- Research quality (default ON for research): key claims = 2 independent sources (else SINGLE-SOURCE);
  expert-benchmark card in parallel with the skeptic.

## Shape
<shape name(s) from shapes.md, plus an ASCII DAG>
  r1(researcher) ─┐
  r2(researcher) ─┼─> v(skeptic) ─> Chief synthesis
  r3(researcher) ─┘

## Cards
| Key | Title | Assignee | Parents | Skills | Model override | Goal mode | Output path |
|---|---|---|---|---|---|---|---|

## Human gates
| When | What Kinshuk decides | Why it's direction-changing |
|---|---|---|

## Budget
Rough: <N> DeepSeek cards (~$0.10-0.50 each), <N> skeptic cards (GLM pool), Chief turns.

## Risks / unknowns
- ...
```
