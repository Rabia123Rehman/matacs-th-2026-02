# Write-up: AI Proposal Triage (MATACS-TH-2026-02)

**Core idea:** AI reads and extracts facts. Plain code decides, scores and ranks. A human confirms and awards.
Diagram: [diagram/process_flow.png](diagram/process_flow.png). Result: [ranking.json](ranking.json).

## 1. AI vs. rules

**AI is used for two things only:**
- **Extraction (step 6).** Proposals are free-form PDFs, so reading "completed 14 installs since 2021" and turning it into `installs = 14` is a language task. Rules cannot do this reliably across different wording.
- **Optional injection classifier (step 5).** A second check for text aimed at AI reviewers, on top of simple pattern rules.

**Everything else is code:** file checks, text extraction, loading criteria, validating evidence, the mandatory pass/fail gate, all scoring formulas, ranking, tie-breaks and logging.

**Why this line:** AI is good at reading messy text and bad at being exactly repeatable and impossible to sweet-talk. Price, weeks and weights are arithmetic, so they belong in code where the admin's weights are applied exactly. The AI never outputs a score or rank. It only returns facts plus a word-for-word quote proving each fact.

## 2. Consistency and explainability

- **Scores come from formulas, not opinion.** Example: price score = weight × lowest eligible price ÷ this price. Fixed formulas for experience, timeline and warranty; a four-item checklist for team (named lead, crew, safety plan, monitoring plan). The formulas live in admin config.
- **Same proposals ranked twice gives the same result.** Scoring is a pure function, so identical facts give identical scores. The one non-deterministic part is the AI, so I use temperature 0, a fixed JSON schema, a pinned model version, and cache the extraction by (text hash, prompt version, model, criteria version). I also run extraction twice on new files and flag any field that disagrees.
- **Evidence is checked by code.** Each extracted fact must carry a quote that exists verbatim in the document. If the quote is not found, the fact is rejected and treated as "not stated". This stops invented facts.
- **A reviewer sees why.** Each proposal shows a score breakdown per criterion, the extracted value, the quote with a link to its page, and a one-line reason built from a template (not free AI text). Missing information is shown as "not stated", never silently guessed.

## 3. Human in the loop

- **Reviewer checkpoint (step 11).** The reviewer sees ranked, flagged and ineligible lists. They can confirm, correct an extracted value (re-scores instantly) or override a rank or eligibility. An override needs a written reason.
- **Flagged items never rank themselves.** Manipulation attempts, unreadable files and conflicting extractions go to a person.
- **The award decision is made by people outside the tool.** The tool only recommends.
- **Audit log:** uploader, file and text hashes, criteria version, prompt version, model and settings, raw AI output, validator results, every score, the ranking, every edit or override with user, time and reason. Logs are append-only.

## 4. Changing criteria

- Criteria are **versioned snapshots**. Every run records the version it used. An edit creates version N+1 and never rewrites N.
- Existing results are marked **"scored under v1, criteria now v2"**. Nothing changes silently.
- Extraction stores *facts*, not scores. A **weight change** therefore needs no new AI call: scoring is re-run on stored facts in seconds and the reviewer sees old versus new ranking.
- A **new or reworded criterion** needs AI extraction for that field only, from the stored text.
- Once a decision is recorded, that run is locked. Changes require a new run.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** (misread number, wrong unit) | Verbatim-quote check, unit normalisation, range checks (price above budget, weeks above 16), double run, reviewer can correct. |
| **Made-up facts** | "Null if not stated" rule, quote must exist in source, otherwise treated as missing. |
| **Prompt injection / manipulation** | Proposal text is wrapped as untrusted data. The AI cannot score, so an instruction like "give full marks" has nothing to act on. Pattern and classifier flags send the file to a human. Sample C is the live example. |
| **Bias** (favouring big firms, polished writing) | Scoring uses only admin-defined criteria, not writing quality. Company names can be hidden from the scorer. |
| **Missing information** | Not guessed. Mandatory items must be explicit. Optional items score zero and show a "clarify with bidder" note. |
| **Over-trust in the ranking** | The UI says "recommendation", flags are prominent, and the human decides. |
| **Cost** | One extraction call per proposal, cached. Re-scoring is free. Page and size limits, and a budget alert. |

## How the sample set comes out

- **A is first (98.0):** passes mandatory checks, best experience, fastest, full team plan.
- **E is second (91.7):** best warranty, but fewer installs and slower than A.
- **D:** D is flagged: no schedule stated, so the 16-week requirement can’t be confirmed. A person should ask the bidder.
- **C is flagged:** its content would score about 84.8, but it contains text trying to manipulate AI reviewers. I ignore that text and send it to a person rather than punishing or rewarding it automatically.
- **B is ineligible:** the cheapest and fastest bid, but the bidder itself does not hold the Ontario electrical licence (a subcontractor is promised after award). Mandatory means mandatory.

## Assumptions

- "Last 5 years" means since 2021. A and C say "since 2021" and "since 2020", so some installs could fall outside the window. The tool counts the stated number and marks it "uncertain" for the reviewer to verify.
- The licence number format is checked by a rule, but real registry verification (ESA/ECRA) is a human or later integration step.
- Ineligible bids are excluded from the "lowest price / fastest" baselines.
