# Paper Specification Gaps & Chosen Resolutions

Log of points where Gelpí, Xue & Cunningham (2025) underspecifies or
appears to contradict itself, and the resolution adopted for this
reproduction. Companion to `notes/environment_spec.md` and
`notes/implementation_checklist.md`.

## Gap 1 — Room graph "contradiction" (RESOLVED — premise revised)

Initial read (implementation_checklist.md Flag #1) held that Appendix A.3
contradicted Figure 2 / Appendix A.2. Full move-by-move reconstruction shows
they reconcile exactly under a room-numbering mapping (A.2 rooms 3/4 = A.3
rooms 4/6; restaurants = A.3 rooms 3/5/7).

**Resolution:** keep A.3's system prompt verbatim (it's the actual
experimental prompt), implement the environment in A.3's numbering,
translate A.2's trajectories via the documented mapping. See
`notes/environment_spec.md`.

## Gap 2 — Optimal Model action rule is prose-only

Sec 4.3.1 gives: agent moves toward its most-preferred believed-open
restaurant via the most efficient path with probability P(open)(1−ε),
ε=0.01 random-room noise; belief P(open)=0.95 updating to 0/1 on
visibility. Unspecified: how residual probability mass is allocated when
P(open)<1 (presumably recursive fallback to the next-preferred restaurant),
and the distribution of the ε random move. **No softmax/temperature
parameter appears anywhere in the paper.**

**Chosen resolution:** adopt a standard formulation from the Bayesian
inverse-planning literature (Baker et al. lineage), documented as a
reproduction decision, and validate solely against Figure 6's printed
per-trajectory posteriors (the only concrete spec).

*Reviewer note:* implement the literal prose policy first (ε-noise +
belief-weighted recursive preference fallback) before reaching for a
Boltzmann softmax — the prose model may reproduce Figure 6 without any
extra parameter; add softmax only if it doesn't. Also: verify Figure 6's
column ordering visually (see environment_spec.md caution #3) before
treating it as ground truth.

## Gap 3 — Validation scope: GPT-4o-mini numbers exist only for Study 2

Study 1 (Sec 4.2.1) and Section 4.5 used GPT-4o (and Gemma 2 for Alice).
Only Study 2 (Sec 4.3.1's LLM list, Tables 2–5) includes GPT-4o-mini.

**Resolution:** run GPT-4o-mini throughout; Study 2 is the quantitative
anchor (Tables 2–5 GPT-4o-mini rows: r=0.960, ρ=0.947, JSD=0.022,
Hellinger=0.146 for LAIP Full). Study 1 and 4.5 succeed on
qualitative/relative-ordering criteria only: LAIP beats baselines, and
posterior mass moves to the correct hypotheses at the correct timesteps.

## Gap 4 — Section 4.5 underspecification

(a) The cosine-similarity embedding model behind `S(O, A_i)` is never
named. **Resolution:** use a standard, explicitly named sentence-embedding
model, recorded in the run notes as a reproduction decision.

(b) The text and Fig. 10 give 4 scenes, but Figure 5 plots t=1…5.
**Resolution:** follow Figure 5. *Likely reconciliation:* t=1 is the
initial prior (before any scene) and t=2–5 are the four scene updates —
adopt that interpretation unless the data contradicts it.

---

*The two already-known rough edges — ρ≥.519 vs Table 3's 0.544 minimum, and
the t(14) d.o.f. mismatch — remain tracked in CLAUDE.md and
implementation_checklist.md; they're reporting quirks, not implementation
blockers.*
