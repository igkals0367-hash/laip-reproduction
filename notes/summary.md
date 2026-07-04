# LAIP Reproduction — Paper Summary

Paper: Gelpí, Xue & Cunningham (2025), *Towards Machine Theory of Mind with
Large Language Model-Augmented Inverse Planning*, arXiv:2507.03682.

## Step 2 — The four questions (from the reproduction guide)

**1. What problem is the paper solving?**
Machine Theory of Mind. Two existing approaches each have a fatal flaw:
Bayesian inverse planning is rigorous and predicts human ToM judgments well
but needs a hand-written hypothesis space (doesn't scale); LLMs handle
open-ended scenarios but are brittle (meaning-preserving rephrasings collapse
accuracy). LAIP combines them.

**2. What dataset(s) does it use?**
- Restaurants task (Studies 1 & 2): hand-authored grid world, Appendix A.2.
  NOT a downloadable dataset — reconstructed from the paper.
- Carol/Alice open-ended scenario (Section 4.5): hand-authored, qualitative.
- MMToM-QA (Section 4.4): public benchmark — EXCLUDED from this reproduction.

**3. What model does it propose?**
LAIP: the LLM generates hypotheses and estimates action likelihoods, while the
posterior update is computed analytically via Bayes' rule (not by the LLM).

**4. How is performance evaluated?**
Correlation (Pearson r, Spearman rho) and distributional distance (JSD,
Hellinger) against an analytic Optimal Model, plus posterior mass on target
hypotheses (Figures 3, 5) and Cohen's d for the model-size analysis.

## Known paper rough edges (caught during reading)
- rho >= .519 claim doesn't reconcile with Table 3 min of 0.544
- t(14) d.o.f. mismatch with 10 trajectories
- H_k vs H_i typo in Algorithm 1 — implement the correct version
