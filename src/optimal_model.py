"""
optimal_model.py
================

The Optimal Model (Study 2) — a purely analytic Bayesian inverse planner over
the fixed 6-hypothesis space. No LLM involved; this is the ground-truth
reference distribution that LAIP and the baselines are scored against via
correlation (Pearson r, Spearman rho) and distance (JSD, Hellinger) metrics.

Two parameters (per the reading sessions): a rationality/softmax parameter and
an epsilon for action noise. epsilon exists so the model never assigns exactly
zero likelihood to an observed action (which would break the Bayesian update).
"""

# TODO: implement analytic Bayesian inverse planning over the 6-hypothesis space
