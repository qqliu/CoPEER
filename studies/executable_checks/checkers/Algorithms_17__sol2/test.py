#!/usr/bin/env python3
"""
Counterexample search for record Algorithms_17__sol2.

TARGET CLAIM (quoted verbatim from the source proof):

    "While the set of edges is unique for a single isolated 2-cycle, the
    theorem holds generally for graphs with cycles because the presence of
    cycles typically allows for variations (like reversing the cycle
    direction) in larger components or when interacting with other parts of
    the graph."

ANALYSIS OF REFUTABILITY
------------------------
The claim as stated is NOT a self-contained mathematical proposition:

  (a) It asserts that "the theorem holds generally", but the theorem itself
      is never stated in the claim text.  Without the theorem's statement we
      cannot test whether it "holds" on any graph.
  (b) It uses the hedge "typically allows for variations", which is not a
      universally or existentially quantified statement over any defined
      finite structure; "typically" has no truth condition we may check.
  (c) "variations ... in larger components or when interacting with other
      parts of the graph" names no precise object (variations of WHAT set,
      under WHAT equivalence).

Hence the full claim is CLAIM_NOT_FINITELY_REFUTABLE.

CONCRETE FRAGMENT WE *CAN* CHECK EXACTLY
----------------------------------------
The claim contains one precise, self-contained factual assertion pair:

  (F1) For a single isolated directed 2-cycle, the edge set is unique:
       reversing the direction of a 2-cycle yields the SAME edge set.
  (F2) For larger cycles (length k >= 3), reversing the cycle direction is a
       genuine "variation": it yields a DIFFERENT edge set.

Both are finitely checkable per cycle length with exact integer arithmetic.
We exhaustively sweep k = 2..12 (labelled directed k-cycles on vertices
0..k-1, edges (i, (i+1) mod k)), compare the edge set of the cycle with the
edge set of its reversal, and search for a counterexample to (F1)+(F2), i.e.
   - a k = 2 cycle whose reversal gives a different edge set, or
   - a k >= 3 cycle whose reversal gives the same edge set.

No floats, no randomness; fixed iteration order over k.
"""

def cycle_edges(k):
    """Edge set of the canonical directed k-cycle on vertices 0..k-1."""
    return frozenset((i, (i + 1) % k) for i in range(k))


def reversed_edges(edges):
    """Edge set of the reversed orientation."""
    return frozenset((v, u) for (u, v) in edges)


def main():
    K_MIN, K_MAX = 2, 12
    witness = None
    for k in range(K_MIN, K_MAX + 1):
        e = cycle_edges(k)
        r = reversed_edges(e)
        same = (e == r)
        expected_same = (k == 2)
        print("k=%2d  edge set == reversed edge set: %-5s  (fragment expects %s)"
              % (k, same, expected_same))
        if same != expected_same:
            witness = (k, sorted(e), sorted(r))
            break

    print()
    if witness is not None:
        k, e, r = witness
        print("WITNESS_FOUND (for the concrete fragment): k=%d" % k)
        print("  cycle edges    :", e)
        print("  reversed edges :", r)
        print("  This contradicts the claim's concrete fragment about")
        print("  uniqueness/variation of edge sets under cycle reversal.")
    else:
        print("NO witness in the swept space k=2..12: the concrete fragment")
        print("holds exactly (2-cycle reversal preserves the edge set; every")
        print("k>=3 cycle reversal changes it).")
        print()
        print("VERDICT: CLAIM_NOT_FINITELY_REFUTABLE")
        print("  The full claim references an unstated 'theorem' and uses the")
        print("  non-quantified hedge 'typically allows for variations', so it")
        print("  is not a self-contained finitely checkable proposition. The")
        print("  only precise fragment it contains was exhaustively verified")
        print("  above with exact integer arithmetic and admits no witness.")


if __name__ == "__main__":
    main()
