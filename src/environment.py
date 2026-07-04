"""
environment.py
==============

The Restaurants task environment (Studies 1 & 2), reconstructed from
Appendix A.2 of Gelpí, Xue & Cunningham (2025).

There is NO downloadable dataset for this task — it is a small hand-authored
grid world. This module encodes:
  - the room/restaurant layout
  - visibility rules (what the agent can see from each location, which drives
    the partial-observability that makes the ToM inference nontrivial)
  - the 10 trajectories used in Study 2 (and the 2-trajectory subset for Study 1)

Everything here is deterministic ground-truth structure, not model output.
"""

# TODO: encode room layout, visibility rules, trajectory list from Appendix A.2
