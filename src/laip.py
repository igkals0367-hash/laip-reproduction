"""
laip.py
=======

The LAIP (LLM-Augmented Inverse Planning) model — the paper's core
contribution, Algorithm 1 (Appendix A.1).

Pipeline per timestep:
  1. LLM generates/maintains hypotheses about the agent's beliefs & desires
  2. LLM estimates action likelihoods P(action | hypothesis, state)
  3. Bayesian update computes the posterior over hypotheses ANALYTICALLY
     (this step is math, NOT delegated to the LLM — that separation is the
     whole point of the method)

Note: Algorithm 1 in the paper has a known H_k vs H_i notation typo (flagged
during the reading sessions) — implement the mathematically correct version.
"""

# TODO: implement Algorithm 1 (hypothesis gen, likelihood, Bayesian update)
