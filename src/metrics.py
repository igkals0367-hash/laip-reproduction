"""
metrics.py
==========

Evaluation metrics used across the studies:
  - Pearson r, Spearman rho  (correlation with Optimal Model)
  - Jensen-Shannon divergence, Hellinger distance  (distributional distance)
  - Cohen's d  (effect size, model-size analysis — may be out of first-pass scope)
  - accuracy / posterior mass on target hypotheses  (Figures 3, 5)

All metrics operate on posterior distributions, so they are model-agnostic:
the same code scores GPT-4o-mini now and Claude Haiku 4.5 later.
"""

# TODO: implement the metric families above
