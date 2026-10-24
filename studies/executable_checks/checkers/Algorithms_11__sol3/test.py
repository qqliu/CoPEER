#!/usr/bin/env python3
"""
Counterexample search — record Algorithms_11__sol3

TARGET CLAIM (quoted verbatim from the proof):

    "and the remaining passengers C2 ∪C3 on the left form an
     independent set"

ANALYSIS OF FINITE REFUTABILITY
-------------------------------
The claim asserts that a specific vertex set C2 ∪ C3 ("the remaining
passengers ... on the left") is an independent set in some graph.  To
search for a concrete counterexample we would need, at minimum:

  1. The graph (its vertex set and edge relation) — e.g., which pairs of
     "passengers" are adjacent, and what adjacency means here (a conflict
     graph? an interval-overlap graph of passenger trips?).
  2. The definitions of the classes C1, C2, C3 — how passengers are
     partitioned, and which of them are "remaining" and "on the left".
  3. Any preconditions established earlier in the proof (e.g., that some
     matching/selection step has already removed certain vertices).

The record supplies ONLY the single quoted sentence fragment.  None of
the objects it mentions (the passenger set, the graph, C2, C3, "left")
is defined in the claim text.  Any bounded search space we could sweep
(e.g., "all graphs on <= n vertices with all 3-colourings of vertices
into C1/C2/C3") would trivially contain 'counterexamples' — e.g., an
edge inside an arbitrarily chosen C2 — but such a witness would refute
only an interpretation WE invented, not the proof's actual claim, since
the proof's C2 and C3 are specific sets produced by its (unquoted)
construction.

Hence the claim, as given, is NOT finitely refutable from the supplied
text: no exhaustive search over any concrete bounded space can be tied
soundly to the claim without inventing the missing definitions.

DEMONSTRATION (why naive instantiation is unsound, not a refutation)
--------------------------------------------------------------------
Below we run a tiny deterministic sweep over all graphs on 3 labelled
vertices and all ways to designate a subset as "C2 ∪ C3".  It finds,
of course, assignments where the designated set is not independent —
which shows the claim is CONTINGENT on the missing construction, i.e.
it cannot be certified or refuted from the fragment alone.  This is
printed for transparency only; it is NOT reported as a witness.

VERDICT: CLAIM_NOT_FINITELY_REFUTABLE
"""

from itertools import combinations, product

VERTICES = (0, 1, 2)
PAIRS = tuple(combinations(VERTICES, 2))  # (0,1),(0,2),(1,2) — fixed order


def independent(subset, edges):
    return all(not (a in subset and b in subset) for (a, b) in edges)


def main():
    contingent_dependent = 0   # some designation of C2∪C3 is NOT independent
    contingent_independent = 0  # some designation IS independent
    total = 0
    for edge_mask in range(2 ** len(PAIRS)):  # all graphs on 3 vertices
        edges = tuple(p for i, p in enumerate(PAIRS) if (edge_mask >> i) & 1)
        for r in range(len(VERTICES) + 1):
            for c23 in combinations(VERTICES, r):  # candidate "C2 ∪ C3"
                total += 1
                if independent(frozenset(c23), edges):
                    contingent_independent += 1
                else:
                    contingent_dependent += 1
    print("Deterministic sweep: all 8 graphs on 3 vertices x all 8 subsets")
    print(f"  total (graph, subset) pairs        : {total}")
    print(f"  subset independent in that graph   : {contingent_independent}")
    print(f"  subset NOT independent in that graph: {contingent_dependent}")
    print()
    print("Both outcomes occur, so the truth of 'C2 ∪ C3 is independent'")
    print("depends entirely on the unquoted construction of the graph and of")
    print("C2, C3 — data the claim text does not supply.  No sound bounded")
    print("counterexample search exists for the fragment as given.")
    print()
    print("VERDICT: CLAIM_NOT_FINITELY_REFUTABLE")
    print("  The quoted claim references undefined objects (the passenger")
    print("  graph, the classes C2 and C3, and the notion 'on the left').")
    print("  Without their definitions, no concrete finite search space can")
    print("  be constructed whose members instantiate the actual claim, and")
    print("  no witness found in an invented space would refute the proof.")


if __name__ == "__main__":
    main()
