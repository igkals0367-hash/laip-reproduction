# LAIP Reproduction — Roadmap & TODO

Governing checklist for reproducing Gelpí, Xue & Cunningham (2025),
arXiv:2507.03682. Adapted from the "Reproduce a Machine Learning Research
Paper" guide (Steps 4–9) for this project's reality: an API-orchestration
paper (no training), implemented BY ME with Claude Code as tutor/reviewer.

Rules that apply to every task below:
- I write all implementation code myself. Claude Code explains, guides,
  and reviews — it does not write implementations (per CLAUDE.md).
- One task at a time. Finish, test, review, commit, THEN move on.
- After each completed task: update CLAUDE.md "Current state", then
  `git add .` → `git commit -m "..."` → `git push`.
- No API-spending task starts before its zero-cost prerequisites pass review.

---

## Phase 0 — Step 4: Break the paper into tasks  ✦ no cost

**Task 0.1 — Generate the implementation checklist with Claude Code.**
The paper PDF must be in `paper/`. Then, in Claude Code:

```
Read paper/paper.pdf and notes/PROJECT_SCOPE.md.

Do NOT write any code. Summarize Algorithm 1 (Appendix A.1) in plain
language, then break the in-scope studies (Study 1, Study 2, Section 4.5)
into an implementation checklist ordered from easiest to hardest.
For each item, cite the paper section/appendix it comes from and state
what "done" looks like. Flag anything underspecified in the paper.
```

Compare its checklist against this roadmap. Where they disagree,
understand why before proceeding — disagreement means either the roadmap
or my paper-understanding has a gap. Save the merged result as
`notes/implementation_checklist.md`.

**Definition of done:** checklist saved, disagreements resolved, committed.

---

## Phase 1 — Zero-cost foundations (Step 5 begins)

Order matters: everything here is deterministic and testable for free,
and everything later depends on it.

**Task 1.1 — `src/environment.py` (Restaurants world).**
Paper mapping: Appendix A.2.
Implement: room layout, restaurant locations, visibility rules (what the
agent sees from each location — the partial observability that makes ToM
inference nontrivial), the trajectory lists (2 for Study 1: Japanese
Open / Japanese Closed; 10 for Study 2), and state descriptions that will
later be rendered into prompts.
Tutor prompt for Claude Code:

```
Read Appendix A.2 of paper/paper.pdf. Without writing code, explain the
environment's structure: rooms, connections, visibility rules, and how
each trajectory unfolds step by step. Then describe what data structures
would represent this cleanly in Python and why. I will implement it.
```

Test (write it myself): for each trajectory, assert the agent's position
sequence is valid (each move connects adjacent rooms) and print what the
agent can see at each step; hand-check 2–3 steps against the paper's
figure.
**Done when:** all trajectories replay correctly and visibility matches
the appendix. Commit: `Implement environment.py: Restaurants world per Appendix A.2`.

**Task 1.2 — `src/optimal_model.py` (analytic Bayesian inverse planner).**
Paper mapping: Study 2's Optimal Model; Bayesian inverse planning
background (Section 2 / Baker et al. lineage).
Implement: the fixed 6-hypothesis space, softmax-rational action
likelihoods with rationality parameter, epsilon action-noise floor
(prevents zero likelihood on observed actions), and the Bayesian
posterior update over a trajectory.
Why second: it forces me to understand the exact math LAIP delegates to
LLM+Bayes, with no API dependence — and it produces the ground-truth
reference all Study 2 metrics compare against.
Tutor prompt:

```
Without writing code: walk me through how the Optimal Model computes
P(action | hypothesis, state) via softmax rationality, and how the
posterior update works step by step for one concrete trajectory from
environment.py. Explain the role of the rationality parameter and the
epsilon noise floor. I will implement it.
```

Test: posteriors over each trajectory must be valid distributions (sum
to 1, no negatives); for an unambiguous trajectory, posterior should
concentrate on the correct hypothesis; sanity-check one trajectory's
posterior direction against the paper's Figure/描述 of Study 2.
**Done when:** posteriors behave sensibly on all 10 trajectories.
Commit: `Implement optimal_model.py: analytic Bayesian inverse planner`.

**Task 1.3 — `src/metrics.py`.**
Paper mapping: Study 2 evaluation (Tables 2–5): Pearson r, Spearman rho,
Jensen-Shannon divergence, Hellinger distance; posterior mass on target
hypotheses (Figures 3, 5). Cohen's d only if the model-size analysis
enters scope later.
Test: verify each metric on hand-computable cases (identical
distributions → JSD = 0, Hellinger = 0, r = 1; a known small example
computed by hand or with scipy as reference).
**Done when:** unit tests pass. Commit: `Implement metrics.py with unit tests`.

**Task 1.4 — Prompt templates + hypothesis-space configs.**
Paper mapping: Appendix A.3 (Study 1 system prompt, verbatim in paper),
Study 2 hypothesis space, Section 4.5 scenario text (Appendix A.5).
Store as files (e.g. `configs/prompts/`), never hardcoded strings, so
prompts are versioned and diffable.
Claude Code role: cross-check my transcription of the paper's prompts
against the PDF character-by-character (transcription errors here would
silently corrupt every downstream result).
**Done when:** prompts transcribed + verified. Commit:
`Add prompt templates and hypothesis-space configs from Appendices A.3/A.5`.

**⛔ REVIEW GATE 1 (mini Step 7, before any API code).**
In Claude Code:

```
Compare src/environment.py, src/optimal_model.py, and src/metrics.py
against paper/paper.pdf (Appendix A.2, Study 2 setup). Identify anything
missing, inconsistent, or implemented differently. Do not fix anything —
report, and I will fix.
```

Fix everything it correctly flags (verify its claims against the paper —
it can be wrong). Commit fixes. Only then proceed.

---

## Phase 2 — API infrastructure  ✦ pennies

**Task 2.1 — `src/batch_client.py`: OpenAI adapter.**
Implement the `OpenAIBatchClient` against the `BatchClient` ABC:
assemble batch request files, submit, poll, retrieve; persist EVERY raw
response to `data/raw_responses/` BEFORE parsing; track token counts and
running cost. Read model/temperature/seed from `configs/run_config.yaml`.
Keep the `AnthropicBatchClient` stub untouched (Phase 6).
Tutor prompt: ask Claude Code to explain the OpenAI Batch API lifecycle
(file format, submission, polling states, result retrieval) and the
error cases to handle — then implement myself, consulting the official
OpenAI docs.
Test: a 2-request batch with a trivial prompt ("reply with the word
'ok'"). Costs a fraction of a cent. Confirm: raw responses land on disk,
token counts logged.
**Done when:** the trivial batch round-trips. Commit:
`Implement OpenAIBatchClient with raw-response logging`.

**Task 2.2 — Response parsing + validation.**
The likelihood-elicitation responses must parse into numbers reliably.
Implement: JSON extraction from model output, schema validation, and a
quarantine path — unparseable responses get logged and flagged, never
silently dropped or guessed.
Test: feed it deliberately malformed outputs (truncated JSON, prose
preamble, wrong keys) and confirm each lands in quarantine with the raw
text preserved.
**Done when:** parser survives adversarial inputs. Commit:
`Add response parsing with quarantine for malformed outputs`.

---

## Phase 3 — LAIP core + baselines  ✦ cost-gated

**Task 3.1 — `src/laip.py` (Algorithm 1).**
Paper mapping: Appendix A.1, Sections 3–4. Per timestep: (1) hypothesis
generation/maintenance via LLM, (2) LLM likelihood estimation
P(action | hypothesis, state), (3) ANALYTIC Bayes posterior update — the
update is never delegated to the LLM; that separation IS the method.
Implement the mathematically correct version of the known H_k/H_i typo.
Design decision to settle with Claude Code first (concepts only): how
runs decompose into batch requests (per-timestep? per-trajectory?) given
that later steps condition on earlier context.
Dry-run test BEFORE spending: a `--dry-run` mode that assembles and
prints all prompts without submitting. Read every prompt; confirm state
descriptions, hypothesis lists, and action options render correctly.
**Done when:** dry-run prompts are correct end to end. Commit:
`Implement laip.py: Algorithm 1 with dry-run mode`.

**Task 3.2 — `src/baselines.py` (Zero-shot, Generic CoT).**
Must reuse laip.py's plumbing/parsing — the ONLY difference between
conditions is reasoning structure, never harness. Dry-run test likewise.
**Done when:** dry-run confirms prompts differ from LAIP only where the
paper says they should. Commit: `Implement zero-shot and generic CoT baselines`.

**⛔ REVIEW GATE 2.** Claude Code review of laip.py + baselines.py against
Algorithm 1 and the study descriptions, same protocol as Gate 1. Also:
re-read my own dry-run prompts against Appendix A.3 one final time.
Nothing proceeds to paid runs until this gate passes.

---

## Phase 4 — Step 6: Run experiments & reproduce results  ✦ main spend (~$3–7 total)

**Task 4.1 — Pilot.** Per `run_config.yaml`: 1 trajectory × 2 runs,
LAIP config, GPT-4o-mini, Batch API. Then:
- Verify raw responses, parsed posteriors, logs all landed
- Compute actual cost per run from token counts; extrapolate the full
  Study 1 + Study 2 spend; write the number into `notes/cost_log.md`
- Eyeball the pilot posterior: does it move in a sensible direction?
**Abort criterion:** if extrapolated full-run cost exceeds ~$10, stop and
re-plan (batch decomposition, prompt lengths) before continuing.

**Task 4.2 — Study 1 full run.** 2 trajectories (Japanese Open/Closed) ×
10 runs × 3 configs (LAIP, Zero-shot, Generic CoT). Store parsed
posteriors in `data/results/`. Compare posterior trajectories
qualitatively against the paper's Study 1 figures — same direction? same
crossover points where belief shifts?

**Task 4.3 — Study 2 full run.** 10 trajectories × 5 runs × 3 configs.
Then score everything with metrics.py against optimal_model.py:
Pearson r, Spearman rho, JSD, Hellinger — my versions of Tables 2–5.

**Task 4.4 — Section 4.5 (Carol/Alice).** Qualitative: run LAIP on the
4 scenes, examine generated hypotheses and posterior evolution, compare
against the paper's narrative description. No metrics.

**Task 4.5 — Document results (guide Step 6 checklist, adapted).**
In `notes/results.md`: all metric tables side by side with the paper's
numbers; run counts; model + API versions and dates; total cost; fixed
temperature/seed; and a DIFFERENCES section explaining every gap
(expected sources: GPT-4o-mini vs the paper's GPT-4o, API model drift
since the paper, residual prompt ambiguities, sampling variance).
Explaining WHY results differ is part of the project, not a failure.

Commits throughout: one per completed run + analysis, e.g.
`Run Study 1 (GPT-4o-mini, batch): posteriors + comparison notes`.

---

## Phase 5 — Step 7: Full review

**Task 5.1 — Claude Code implementation audit.**

```
Compare my full implementation in src/ against the methodology in
paper/paper.pdf. Check especially: Algorithm 1's update math, prompt
fidelity to Appendix A.3, the optimal model's likelihood function, and
metric definitions. List anything missing, inconsistent, or implemented
differently, ordered by how much it could affect results. Do not fix
anything — I will.
```

**Task 5.2 — Discrepancy triage.** For each flagged item: verify against
the paper myself, classify as (bug → fix and re-run affected results) /
(deliberate documented deviation → ensure it's in results.md) / (false
positive → note and dismiss). Re-run anything a bug invalidated.

---

## Phase 6 — Step 8: Extension (already scoped)

**Task 6.1 — `AnthropicBatchClient`.** Implement the second adapter
against the same ABC. Trivial-batch test as in Task 2.1.
**Task 6.2 — Claude Haiku 4.5 generalization run.** Identical harness,
identical prompts, only the model changes. Re-score with metrics.py.
**Task 6.3 — Cross-model analysis in results.md:** does LAIP's advantage
over baselines transfer across model families? This is the reproduction's
genuine contribution beyond the paper.

---

## Phase 7 — Step 9: Publish

**Task 7.1 — Final README:** overview, paper link, honest scope
statement (what was and wasn't reproduced), setup instructions
(.env.example flow), results tables vs paper, differences discussion,
what I learned, future work (e.g. MMToM-QA as the natural unreproduced
extension).
**Task 7.2 — Repo hygiene pass:** decide whether `data/raw_responses/`
stays tracked (size vs full auditability), confirm no secrets anywhere in
history, check the repo clones-and-runs from the README instructions
alone.

---

## Standing per-task loop (memorize this)

1. Read the relevant paper section myself first
2. Tutor prompt to Claude Code — concepts, mapping, pitfalls; no code
3. Implement it myself
4. Test it (free tests always precede paid tests)
5. Ask Claude Code to review the diff against the paper
6. Fix, update CLAUDE.md "Current state", commit with a descriptive message, push