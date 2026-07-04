# LAIP Implementation Checklist (from a full read of paper/6. TOWARDS.pdf)

Produced per ROADMAP Task 0.1. No code written — concepts, mapping, and
flags only.

## Algorithm 1 (Appendix A.1) in plain language

Per timestep `t`, over a fixed set of hypotheses H about the target agent's
beliefs/desires:

1. **Get the prior.** At `t=0`, the LLM generates a prior `P(H)` from scratch
   given the initial world state. At every later step, the prior is just
   last step's posterior: `P(H) ← P(H|A_{t-1})`. This is standard sequential
   Bayesian updating — the posterior becomes the next prior.
2. **For each hypothesis, imagine the action.** For each `H_i`, the LLM
   generates a set of plausible candidate actions `{A_1...A_N}` the agent
   might take *if that hypothesis were true*, given the current state. This
   is the "if agent believed/wanted X, what would it do here?" step.
3. **Score each action under each hypothesis.** For each candidate action,
   the LLM estimates `P(A_j | H_i)` — a separate likelihood call. Across all
   hypotheses this produces a likelihood matrix (hypotheses × actions).
   (Study 2 text adds a detail Algorithm 1 doesn't state explicitly: these
   per-hypothesis action probabilities are then normalized to sum to 1.)
4. **Observe the real action.** The agent actually acts; the harness (or an
   LLM call, `llm_observe()`) records the ground-truth action `O`.
5. **Update analytically.** `P(H|O) ∝ P(A|O) · P(A|H) · P(H)` — Bayes' rule.
   `P(A|H)·P(H)` is the standard likelihood-times-prior. `P(A|O)` is doing
   the work of mapping the observed action onto the LLM's *generated*
   candidate actions — in Studies 1/2 this is trivial (O is drawn from a
   small enumerated action space, so it's essentially a lookup/indicator).
   In Section 4.5's open-ended version, this term is replaced by
   `softmax(cosine_similarity(O, A_i))` because O is free text that won't
   exactly match any generated `A_i` (see Section 4.5's explicit formula).
   Per CLAUDE.md and the paper's own Full-model description, this step must
   be computed **mathematically**, never delegated to the LLM — that's the
   entire point of the hybrid design (the "LLM computes posterior" variant
   is a different, out-of-scope configuration used only for comparison).
6. Loop back to step 1 with the new posterior as next prior; after `t=T`,
   return the final `P(H|O)`.

**Confirmed typo (per CLAUDE.md):** line 9 of the printed algorithm calls
`generate_llm_actions(S, Hk)` inside a loop over `H_i in H` — should read
`H_i`, not `H_k`. Implement the loop variable consistently as `H_i`.

---

## Checklist, easiest → hardest

### Tier 1 — Deterministic, zero-cost, no LLM

**1. Environment model** — Study 1 & 2 (shared). Cites: Sec 4.1 (task
description), Fig. 2 (Study 1 schematic), Appendix A.2 (trajectory table),
Appendix A.3 (Study 1 system prompt — this is where the *actual* room graph
and visibility rules are spelled out, not Appendix A.2).
**Done when:** all 12 trajectories (2 Study-1 + 10 Study-2) replay as valid
room-to-room moves, and visibility/open-closed state at each timestep can be
printed and hand-checked against the paper's descriptions.
Note: Figure 2/A.2 and A.3 use different room numberings for the same
environment (originally misread as a contradiction — see Flag #1 below,
now resolved). Implement from the reconciled spec in
`notes/environment_spec.md`.

**2. Optimal Model** — Study 2 only. Cites: Sec 4.3.1 "Optimal Model"
paragraph; Appendix A.2 Fig. 6 gives the actual numeric posterior for every
one of the 10 trajectories over the 6 hypotheses (the 6 total orderings of
{Japanese, Chinese, Mexican}).
**Done when:** your implementation reproduces Fig. 6's printed values (e.g.
Trajectory 1 → 0.661 on `J>C>M`) to reasonable rounding, for all 10
trajectories.
⚠️ **See Flag #2 — the model's action-selection rule is under-specified as
prose, not a formula; you'll likely need to reverse-engineer the missing
piece against Fig. 6's numbers.**

**3. Metrics module** — Study 2 evaluation. Cites: Sec 4.3.2, Appendix A.4
(Tables 2–5: Pearson r, Spearman ρ, JSD, Hellinger). Purely mathematical,
no dependency on anything above except needing two distributions to compare.
**Done when:** hand-computable cases pass (identical distributions → r=1,
JSD=Hellinger=0), matching scipy reference values.

### Tier 2 — Prompt transcription (no LLM calls yet, but paper-fidelity-critical)

**4. Study 1 prompts** — verbatim in the paper. Cites: Appendix A.3, Fig. 8
(system prompt + hypothesis-generation prompt for Study 1, character-for-
character).
**Done when:** transcription matches the PDF exactly (spacing, phrasing,
the 7-room list, the visibility bullets).

**5. Study 2 prompts** — **not given verbatim anywhere in the paper.** Cites:
Sec 4.3.1's prose descriptions of each configuration (LAIP Full, Generic
CoT, Zero-Shot Baseline) — this is the only source. You'll be
reconstructing prompts from a paragraph of description, reusing the Study 1
environment description as the base, with the hypothesis space now fixed to
the 6 total preference-orderings instead of 20 LLM-generated hypotheses.
**Done when:** prompts are internally consistent with Sec 4.3.1's
description of what info the LLM receives at each configuration.

**6. Section 4.5 prompts** — partially given. Cites: Appendix A.5, Fig. 10
(situation prompt + 4 scene texts, verbatim), but the *per-step* hypothesis-
generation and 6-candidate-action-generation prompts are only described in
prose in Sec 4.5, not shown.
**Done when:** situation/scene text matches Fig. 10 exactly; per-step
prompts are a reasonable reconstruction of Sec 4.5's description.

### Tier 3 — LAIP core (dry-run only, still zero-cost)

**7. `laip.py` — Algorithm 1, dry-run mode.** Cites: Sec 3, Appendix A.1.
Depends on Tiers 1–2 above being settled, since prompts render state/
hypotheses/actions into text.
**Done when:** `--dry-run` prints every assembled prompt for a full
trajectory without calling any API, and it reads correctly against
Appendix A.3/Sec 4.3.1.

**8. Baselines (`baselines.py`) — Zero-shot, Generic CoT.** Cites: Sec
4.3.1's Generic CoT / Zero-Shot Baseline paragraphs. Must reuse `laip.py`'s
plumbing.
**Done when:** dry-run prompts differ from LAIP only in reasoning
structure (presence/absence of the "think step by step" instruction, single
call vs. per-hypothesis calls), never in harness details.

### Tier 4 — Paid runs, ordered by how directly they're checkable against the paper

**9. Study 2 full run (GPT-4o-mini).** Cites: Sec 4.3, Appendix A.4 Tables
2–5. **This is the only in-scope study where the paper published GPT-4o-mini
numbers you can validate against** (r=0.960, ρ=0.947, JSD=0.022,
Hellinger=0.146 for LAIP Full/GPT-4o-mini). Do this validation before
trusting the harness for Study 1 or 4.5.
**Done when:** your Study 2 GPT-4o-mini metrics are in the same neighborhood
as the paper's GPT-4o-mini row, for the three in-scope configurations
(LAIP Full, Generic CoT, Zero-Shot Baseline — the paper's other two LAIP
variants and non-GPT/non-Claude LLMs are out of scope per PROJECT_SCOPE).

**10. Study 1 full run (GPT-4o-mini).** Cites: Sec 4.2, Fig. 3.
⚠️ **See Flag #3 — the paper's Study 1 numbers (48.4% etc.) are GPT-4o
only; there is no published GPT-4o-mini baseline for Study 1.** "Done" here
can only mean *qualitative* agreement (does posterior mass concentrate on
H2 when Japanese is closed; does it stay diffuse when open; does the
sharpest belief shift land between timesteps 2→3) — not a numeric match.

**11. Section 4.5 (Carol/Alice), qualitative.** Cites: Sec 4.5, Fig. 5,
Fig. 10, Table 6. Hardest, for three reasons: (a) needs the cosine-
similarity action-matching mechanic, which nothing else in this
reproduction uses; (b) no published GPT-4o-mini reference (paper used
GPT-4o for Carol, Gemma 2 for Alice); (c) prompts are the least
fully-specified of the three studies (Tier 2 item 6).
⚠️ **See Flag #4 — the similarity function's embedding model is
unspecified**, and **Flag #5 — a scene-count/timestep-count mismatch.**
**Done when:** LAIP's posterior concentrates more on Alice's true
preferences (H9/H10-equivalent hypotheses) than the zero-shot baseline,
matching the qualitative pattern in Fig. 5/Table 6 — no numeric target.

---

## Flags: underspecified or inconsistent in the paper

**Flag #1 — Room-graph "contradiction" — RESOLVED, original flag was wrong.**
This flag originally claimed Figure 2 / Appendix A.2 and Appendix A.3 were
incompatible (e.g. that Trajectory 3's "Room 2, Room 3, Mexican" was
impossible under A.3's connectivity). That analysis missed that the two
sources use **different room-numbering schemes for the same environment**:
A.3 numbers the restaurant locations as rooms (3 = Chinese, 5 = Mexican,
7 = Japanese), while Figure 2/A.2 number only the four plain rooms 1–4
(A.2 rooms 3/4 = A.3 rooms 4/6). Under that mapping every trajectory is a
legal walk and every visibility statement matches. Full reconciled spec:
`notes/environment_spec.md`; resolution logged as Gap 1 in
`notes/paper_gaps.md`.

**Flag #2 — Optimal Model's action rule is prose, not a formula.**
Sec 4.3.1 states: baseline belief `P(open)=0.95` per restaurant; agent
moves toward its most preferred *available* restaurant via the shortest
path with probability `P(open)(1−ε)`, `ε=0.01` chance of moving to a random
room instead. This doesn't fully specify the model: it doesn't say what
happens with the remaining probability mass when P(open)≠1 exactly (does
the agent instead move toward its 2nd-preferred restaurant weighted by its
belief that the 1st is closed? recursively down the ranking?), nor how
"random room" is distributed among the topology. There's no softmax or
temperature parameter here at all, despite CLAUDE.md's description of a
"rationality/softmax parameter" — as printed, this is a two-parameter
epsilon-greedy belief-weighted policy, not a softmax-over-utilities model.
Practically: use Fig. 6's 10 printed trajectory posteriors as your ground
truth and treat the Optimal Model implementation as validated only once it
reproduces those numbers — the formula in the prose is necessary but not
sufficient to derive them uniquely.

**Flag #3 — Study 1 and Section 4.5 have no published GPT-4o-mini numbers.**
Sec 4.2.1: "Both models used GPT-4o... to generate their responses" (Study
1). Sec 4.5: "using LAIP with GPT-4o" (Carol) / "Gemma 2" (Alice). Only
Study 2 (Sec 4.3.1's LLM list) includes GPT-4o-mini. This changes what
"validate against the paper's published numbers" (CLAUDE.md, model
sequencing) can mean for Study 1/4.5: qualitative pattern-matching only,
not numeric reproduction. Worth updating ROADMAP Task 4.2/4.4's "done"
language to reflect this rather than discovering it mid-run.

**Flag #4 — Section 4.5's cosine-similarity embedding model is unnamed.**
The formula `P(H|O) = softmax(S(O, A_i)) P(A|H) P(H)` (Sec 4.5) requires an
embedding function to compute `S`, but the paper never names one. You'll
need to choose (e.g., an OpenAI embedding endpoint) and document it as a
reproduction-specific decision, not a paper detail.

**Flag #5 — Scene count vs. timestep count mismatch in Section 4.5.**
Sec 4.5's prose says "four individual scenes," and Fig. 10 lists exactly 4
scenes — but Fig. 5's heatmap rows go `t=1` through `t=5` (5 timesteps) for
both LAIP and the baseline. Either a scene was dropped from the text, a
timestep doesn't map 1:1 to a scene, or Fig. 5 has an off-by-one. Worth
resolving before treating Fig. 5/Table 6 as a per-scene target.

**Flag #6 (already known, confirmed on this read) — rho ≥ .519 vs. Table 3.**
Sec 4.3.2 claims "all ρ ≥ .519" for the Full model's correlation with the
optimal model across all 7 LLMs; Table 3's actual minimum in the LAIP
(Full) column is 0.544 (GPT-3.5). No table value is .519. Doesn't block
implementation — just don't chase .519 as a target; 0.544 is the real
minimum to reproduce direction-of-effect against.

**Flag #7 (already known, confirmed on this read) — `t(14)` d.o.f.**
Appendix A.4.1's Cohen's-d comparisons report `t(14)` throughout, implying
paired samples of size 15, but Study 2 has 10 trajectories × 5 runs = 50
observations per model/condition (or 10 trajectory-level means, which would
give df=9, not 14). The paper doesn't explain the aggregation that would
produce n=15. Since Cohen's d/t-tests are flagged in CLAUDE.md as possibly
out of first-pass scope, this can be deferred, but if you do implement it,
don't assume `t(14)` tells you the intended n — derive your own df from
however you structure the paired comparison and document the deviation.
