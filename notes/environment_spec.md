# Restaurants Environment — Reconstructed Specification

Sources: Section 4.1/4.2, Figure 2, Appendix A.2 (trajectory table),
Appendix A.3 (Study 1 system prompt). Produced per ROADMAP Task 0.1 follow-up;
behaviorally cross-validated against Figure 6's optimal-model posteriors.

## The reconciliation (read this first)

Figure 2 / A.2 / Sec 4.2 and Appendix A.3 are **not contradictory** — they
use two different room-numbering schemes for the same environment. A.3
numbers the restaurant locations as rooms (3 = Chinese, 5 = Mexican,
7 = Japanese), while Figure 2/A.2 number only the four plain rooms 1–4.

| Figure 2 / A.2 / Sec 4.2 | Appendix A.3 system prompt |
|---|---|
| Room 1 (start) | Room 1 |
| Room 2 | Room 2 |
| Room 3 | Room 4 |
| Room 4 | Room 6 |
| Chinese restaurant (location) | Room 3 |
| Mexican restaurant (location) | Room 5 |
| Japanese restaurant (location) | Room 7 |

Check against A.3's text, translated: "Room 2 connects to 1, 3, 4" → Room 2
connects to Room 1, the Chinese restaurant, and Room 3 ✓. "Room 4 connects
to 2, 5, 6" → Room 3 connects to Room 2, the Mexican restaurant, and
Room 4 ✓. "Room 6 connects to 4 and 7" → Room 4 connects to Room 3 and the
Japanese restaurant ✓. Section 4.2's "not able to observe whether the
Japanese restaurant is open until reaching Room 3" matches A.3's "Japanese
visible from Room 4" under the mapping ✓.

## 1. Every move in every trajectory (A.2 labels; all start in Room 1)

| Trajectory | Moves (from → to) | World state |
|---|---|---|
| Study 1 Open | 1→2, 2→3, 3→2, 2→**eat Chinese** | all open |
| Study 1 Closed | 1→2, 2→3, 3→2, 2→**eat Chinese** | Japanese closed |
| 1 | 1→2, 2→3, 3→2 | Japanese closed |
| 2 | 1→2, 2→3, 3→4 | all open |
| 3 | 1→2, 2→3, 3→**eat Mexican** | all open |
| 4 | 1→2, 2→**eat Chinese** | all open |
| 5 | 1→2, 2→3, 3→4 | Mexican closed |
| 6 | 1→2, 2→**eat Chinese** | Mexican closed |
| 7 | 1→2, 2→3, 3→**eat Mexican** | Chinese closed |
| 8 | 1→2, 2→3, 3→4 | Chinese closed |
| 9 | 1→2, 2→3, 3→2 | all open |
| 10 | 1→2, 2→3, 3→4 | Chinese & Mexican closed |

Note: Trajectories 1 and 9 "correspond to" the Study 1 Closed/Open rows per
Sec 4.3.1 but are one action shorter (no final eat) — treat them as distinct
3-action trajectories, not aliases.

## 2. Adjacency graph (A.2 labels)

A path: **1 – 2 – 3 – 4**, plus one restaurant hanging off each of rooms
2/3/4: **2 – Chinese, 3 – Mexican, 4 – Japanese.** No 1–4 connection
(Figure 2 draws the rooms in a 2×2 grid, but nothing connects 1 and 4, and
A.3 lists no such edge).

Per-room action space:

- Room 1: move to 2
- Room 2: move to 1, move to 3, eat Chinese
- Room 3: move to 2, move to 4, eat Mexican
- Room 4: move to 3, eat Japanese

Eating = entering the restaurant location; only legal if that restaurant is
open. Episodes end on an eat action (or at the last listed move).

## 3. Restaurant visibility (status observable from — A.2 labels, from A.3 translated)

| Restaurant | Visible from | Not visible from |
|---|---|---|
| Chinese | Rooms 1, 2, 3 | Room 4 |
| Mexican | Rooms 2, 3, 4 | Room 1 |
| Japanese | Rooms 3, 4 | Rooms 1, 2 |

Agent belief rules (Sec 4.1, 4.3.1): prior belief P(open) = 0.95 per
restaurant; when a restaurant becomes visible, belief snaps to 1 or 0;
closed restaurants never reopen; closed restaurants can't be eaten at.

**Behavioral cross-validation against Figure 6** (this is what confirms the
visibility table): Trajectory 6 (eat Chinese immediately, Mexican closed)
puts high posterior on M-first-then-C — only coherent if the agent saw
Mexican closed *from Room 2*, exactly as the table says. Trajectory 1's
0.661 on J>C>M requires Japanese observable from Room 3 ✓. Trajectory 10
(both alternatives closed) is uniform 1/6 — everyone's only option is
Japanese ✓.

## 4. Divergences / cautions

1. **No substantive divergence from A.3 after the mapping** — the
   "contradiction" was a numbering clash. Consequence for implementation:
   **A.3's system prompt is the verbatim experimental artifact and uses the
   7-room numbering, so prompts must render states in A.3's scheme.**
   Recommendation: implement `environment.py` natively in A.3's 7-location
   numbering and translate A.2's trajectory table once at data-entry
   (mapping above), rather than maintaining two schemes at the LLM boundary.
2. Figure 2 is a simplified schematic (2×2 grid with restaurant diamonds);
   its geometry should not be treated as adjacency — the graph above is
   derived from A.3 + trajectory legality.
3. PDF text extraction of Figure 6 shows the M>J>C / M>C>J columns in an
   order inconsistent with behavioral logic on trajectories 5 and 6 (the
   two values appear swapped). Almost certainly a text-layer artifact
   rather than a paper error, but **verify the column mapping against the
   rendered figure before using Figure 6 as the optimal-model validation
   target.**
