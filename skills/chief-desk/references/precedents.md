# Precedents: shapes that worked (append one entry per project in the retro)

Not playbooks. Starting points Chief adapts. Format:
`## <date> <slug>` · ask · tier · shape · roster · what worked · what to change.

## 2026-10-22 jev-integration-facts (pilot, verified)
- Ask: can Jev be wired in as a cheap judge? Tier T2. Shape: fan-out (2 researchers, sliced
  API/SDK vs access/price/terms) → skeptic → Chief synthesis. 12 min wall clock;
  DeepSeek $0.34 + GLM ~$0.20.
- Worked: non-overlapping slices with "do NOT cover X" lines; ledger format stamped in every
  card; `dir:` workspace; the parent gate auto-promoted the skeptic.
- Change: verify cards must retry rate-limited fetches and report "UNCHECKED (rate-limited)"
  separately from WEAK. Chief still spot-checks key claims live (it caught a WEAK one that was actually SUPPORTED).

## 2026-10-24 oxygen-enriched rooms v3 (technical brief for Kinshuk's dad, verified)
- Shape: 4 researchers (one per question the dad asked) ∥ benchmark (no parents: nothing to compare yet;
  Chief compared at acceptance) → skeptic → Chief sizing maths + writing. 34 min of card time; DeepSeek
  $1.83 + GLM ~$0.67. Primary share 64% (first run to meet 60%).
- Worked: one card per reviewer question; Chief's own arithmetic section (a sizing table) made the specs
  usable; live checks with jev_check's fetcher caught a misread Chinese "maximum" and an invented
  local-content split.
- Didn't: skeptic passed 150 rows on "researcher verified" because jev-judge couldn't read PDFs. Fixed
  the tool (PDF + Parliament items), not just the rule. Firecrawl credits ran low mid-run: check before
  dispatch (`tools/firecrawl_credits.py`).

## 2026-10-23 high-altitude-shelters v2 (upgrade to the new research standard, verified)
- Shape: d1 + d2 (dig-deeper researchers on 22 listed key claims) ∥ b (expert benchmark) → skeptic
  (new rows only) → Chief revision. 34 min of card time, DeepSeek $0.81 + GLM $0.38.
- Worked: Chief diagnosed every "won't load" site BEFORE dispatch and shipped a tool
  (`~/ChiefDesk/tools/gov_sources.py`) + `ACCESS_ROUTES.md`; Parliament's e-library gave the best
  primaries of the project. The benchmark card found the decisive market fact (Army closed its shelter
  project because off-the-shelf modular shelters won). Primary share 46% → 58%.
- Didn't: skeptic accepted "parent-verified" rows it couldn't fetch, over-applied the expiry check (DAP)
  and missed a real expiry (emergency route). Chief caught both live. Fixed in the skeptic card template.

## 2026-10-23 high-altitude-shelters (first desk report, verified)
- Ask: private business brief, could Kinshuk build/sell breathing shelters to India's defence forces?
  Tier T2. Shape: 3 researchers (tech+images / India-vs-China premise / buyers+routes) → skeptic with
  jev-judge pre-pass → writer → Chief acceptance and HTML+PDF. ~$1.55 workers, ~1 h of card time.
- Worked: premise-check slice (his premise was half wrong); skeptic hand-checks overturned Jev's false
  negatives; Chief live re-check of 5 claims caught 2 errors the skeptic passed.
- Change: wake-on-completion does NOT fire for desktop sessions (see Step 5); old-vs-new tables need
  column-by-column reading; image relevance needs Chief's eye; render and look at every PDF page.

## 2026-10-23 jev-judge build (T0, verified)
- Ask: build the Jev judge, calibrate, wire into skeptic and writer. Tier T0: Chief built it
  directly; the known-answer calibration set was the independent check (no producer/checker split needed).
- Worked: following the vendor's own cookbook (citation check: string-match first, then one
  Choice with a 0.8 gate) instead of the planned single noul; passing the source URL into state;
  smoke-testing each worker with a prompt that did NOT mention the skill, to prove the soul wiring.
- Change: calibrate with 3 repeats, not 1 (Jev drifts up to 0.2 at low confidence). Total Jev
  spend for all calibration + tests: under $0.005; skeptic smoke test ~$0.03 of the GLM pool.

## Seed sketches (unverified; replace with real entries as projects run)
- **Background research on a person (public sources)**: T2. Fan-out by facet (career
  timeline, published work/talks, company context, recent news) → skeptic → Chief brief.
- **Article**: T2. Researcher fan-out (if factual) → writer draft (kinshuk-essay-voice) →
  skeptic (facts + AI tells) → Chief voice pass. Human gate: angle/thesis before drafting.
- **Humanize a draft**: T0/T1 for short text; T2 for long: writer (humanizer +
  kinshuk-essay-voice) → skeptic AI-tell scan → loop until clean.
- **Strongest job application**: T2. Researcher (company, team, role, recent news) +
  Chief maps JD to Kinshuk's stories (kinshuk-context) → writer → skeptic → Kinshuk sends.
- **Tool that speeds up his own applications**: T2. Maker builds tailoring + tracker +
  form prefill with dry-run and per-application approval; review loop; Chief runs it live.
- **Clone software to learn it**: T2. Maker with `reverse-engineer-anything` (+
  `web-effect-forensics` for visuals): evidence → observed/inferred/unknown map → Kinshuk
  picks rebuild scope (gate) → maker rebuilds → Chief side-by-side check.
- **Interview prep**: T2. Researcher (company, interviewer public profiles, as-of dated)
  → Chief skill map vs JD → writer/coach question bank from his real stories → skeptic → live mock in chat.
- **Study a topic**: T2. Researcher (current sources) → maker builds visual HTML lessons +
  quizzes → cron job for spaced repetition review.
- **Recreate a data-API product (e.g. Mindcase)**: T2. Legality gate first (per-source ToS/law
  → skeptic → Chief marks buildable sources; human gate on scope) ∥ maker+REA on the
  competitor's own public app (catalog, run model, pricing, MCP surface) ∥ researcher on
  building blocks (official APIs, licensed vendors, OSS) with cost per record → one v1 build
  of the core runner (Build rule) → maker cards per buildable source + MCP server + metering,
  Jev for dedupe/validation inside → review → Chief live test. Sources with no permitted
  route are dropped and named, not worked around.
- **Browser game (e.g. GTA-style three.js)**: T2 with the Build rule. Acceptance tests
  (controls, FPS, features, bug list) → one v1 build (Chief on Opus if it fits) → researcher
  (libs, free assets, physics) → maker feature/perf cards on v1 in worktrees → playtester
  (mint on first use) plays via browser + screenshots → merge what passes the tests. A
  competing second build only if Build rule step 4 holds (gate). If learning: coach walks
  through the architecture.
