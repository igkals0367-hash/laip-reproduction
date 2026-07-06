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

ADJACENCY = {
    1: frozenset({2}),
    2: frozenset({1,3,4}),
    3: frozenset({2}),
    4: frozenset({2,5,6}),
    5: frozenset({4}),
    6: frozenset({4,7}),
    7: frozenset({6})
}

RESTAURANT_LOCATIONS = {
    3: "Chinese",
    5: "Mexican",
    7: "Japanese"
}

VISIBILITY = {
    "Chinese": frozenset({1,2,4}),
    "Mexican": frozenset({2,4,6}),
    "Japanese": frozenset({4,6})
}

for room, neighbors in ADJACENCY.items():
    for n in neighbors:
        assert room in ADJACENCY[n], f"asymmetric edge {room} ->{n}"

