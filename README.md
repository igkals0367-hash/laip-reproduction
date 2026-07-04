# Reproducing LAIP: LLM-Augmented Inverse Planning for Machine Theory of Mind

A partial reproduction of Gelpí, Xue & Cunningham (2025),
*Towards Machine Theory of Mind with Large Language Model-Augmented Inverse
Planning*, [arXiv:2507.03682](https://arxiv.org/abs/2507.03682).

## Overview
LAIP is a hybrid machine Theory-of-Mind method: an LLM proposes hypotheses
about an agent's beliefs/desires and estimates action likelihoods, while the
posterior over hypotheses is updated analytically with Bayes' rule. This
separation aims to keep the open-endedness of LLMs while restoring the
reliability of formal Bayesian inference.

## Scope of this reproduction
See `notes/PROJECT_SCOPE.md`. In brief: Studies 1 & 2 (Restaurants task) and
the Section 4.5 open-ended scenario; configs LAIP Full, Zero-shot, Generic CoT,
plus the analytic Optimal Model for Study 2. MMToM-QA is excluded.

Models are run in sequence: **GPT-4o-mini first** (validated against the paper's
published numbers), then **Claude Haiku 4.5** as a generalization test through
the same harness.

## Structure
```
laip-reproduction/
├── paper/                # the paper PDF
├── notes/                # summary.md, PROJECT_SCOPE.md
├── src/                  # environment, laip, baselines, optimal_model,
│                         #   batch_client, metrics
├── data/
│   ├── trajectories/     # hand-authored restaurant trajectories (App. A.2)
│   ├── raw_responses/    # every raw API response, logged before parsing
│   └── results/          # parsed posteriors, metrics, figures
├── configs/              # model settings, hypothesis spaces
└── README.md
```

## Cost control
All LLM calls go through the Batch API (~50% cheaper). A pilot run precedes any
full run to measure real per-run cost. Raw responses are logged so a parsing
bug never requires re-paying for calls. Target: ~$3–7 for the first pass.

## Status
Project scaffolding complete (guide Step 3). Next: implement components one at a
time (guide Step 5), starting with `environment.py`.

## Original paper
Gelpí, R. A., Xue, E., & Cunningham, W. A. (2025). *Towards Machine Theory of
Mind with Large Language Model-Augmented Inverse Planning.* arXiv:2507.03682.
