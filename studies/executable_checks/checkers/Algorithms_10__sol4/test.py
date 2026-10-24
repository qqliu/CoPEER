#!/usr/bin/env python3
"""
BLIND counterexample search — record Algorithms_10__sol4

TARGET CLAIM (quoted verbatim from the proof):

    "(since S ⊇Rm−1, and by construction Rm−1 has no edges to Wm)."

i.e.  "(since S ⊇ R_{m-1}, and by construction R_{m-1} has no edges to W_m)."

WHAT THE CLAIM ASSERTS
----------------------
The fragment is a parenthetical justification consisting of two premises:

  (P1)  S ⊇ R_{m-1}
  (P2)  R_{m-1} has no edges to W_m   ("by construction")

ANALYSIS OF FINITE REFUTABILITY
-------------------------------
Every object in the claim — the set S, the set R_{m-1}, the set W_m, the
graph whose edges are referenced, and the index m — is defined by a
surrounding construction that is NOT contained in the claim text.  The
claim text supplied to this search agent consists of the parenthetical
alone.  In particular:

  * (P1) relates S to R_{m-1}, but neither S nor R_{m-1} is defined here;
    whether S ⊇ R_{m-1} holds is a property of the unstated construction,
    not of any free mathematical variables we could enumerate.
  * (P2) explicitly appeals to "by construction": it is a claim about a
    specific algorithmic construction of R_{m-1} and W_m that the text
    does not provide.  Without the construction there is no predicate to
    test against candidate graphs.
  * The fragment states premises only; it draws no free-standing
    implication of the form "for all X, P(X)" that could be falsified by
    exhibiting a finite witness X.  Any graph/sets (G, S, R, W) we might
    enumerate could trivially violate "S ⊇ R" or "R has no edges to W",
    but such a triple would NOT be a counterexample to the claim, because
    the claim quantifies over nothing: it asserts these properties of the
    particular objects produced by the (absent) construction.

Therefore no bounded exhaustive search over concrete finite structures
can refute (or corroborate) the claim: any candidate structure would
require us to INVENT the construction of R_{m-1} and W_m, which the
claim text does not supply.  Per the search protocol, we must not invent
data the claim does not supply.

SANITY DEMONSTRATION (exact, deterministic, decides nothing)
------------------------------------------------------------
To document that the premises are contingent (i.e. neither tautologies
nor contradictions over unconstrained finite structures — confirming the
claim's truth value genuinely depends on the missing construction), we
exhaustively sweep all triples (S, R, W) of subsets of a 3-element vertex
set together with all graphs on those 3 vertices, and count how many
satisfy / violate (P1) and (P2).  This is NOT a counterexample search for
the claim itself; it only certifies that the premises are non-vacuous and
non-trivial as abstract predicates, hence undecidable without the
construction.

VERDICT: CLAIM_NOT_FINITELY_REFUTABLE
"""

import itertools

RECORD_ID = "Algorithms_10__sol4"


def main() -> None:
    n = 3
    vertices = tuple(range(n))
    all_pairs = tuple(itertools.combinations(vertices, 2))

    subsets = []
    for mask in range(1 << n):
        subsets.append(frozenset(v for v in vertices if (mask >> v) & 1))

    sat_p1 = viol_p1 = 0
    sat_p2 = viol_p2 = 0
    total = 0

    for edge_mask in range(1 << len(all_pairs)):
        edges = frozenset(
            all_pairs[i] for i in range(len(all_pairs)) if (edge_mask >> i) & 1
        )
        for S in subsets:
            for R in subsets:
                for W in subsets:
                    total += 1
                    # (P1) S superset of R
                    if R <= S:
                        sat_p1 += 1
                    else:
                        viol_p1 += 1
                    # (P2) R has no edges to W
                    has_edge_R_W = any(
                        ((u in R and v in W) or (v in R and u in W))
                        for (u, v) in edges
                    )
                    if has_edge_R_W:
                        viol_p2 += 1
                    else:
                        sat_p2 += 1

    print(f"record_id: {RECORD_ID}")
    print("claim: '(since S \\u2287 R_{m-1}, and by construction R_{m-1} "
          "has no edges to W_m).'")
    print()
    print("Sanity sweep over all graphs on 3 vertices x all (S,R,W) subset "
          f"triples: {total} structures examined (exact integer arithmetic, "
          "fixed iteration order).")
    print(f"  premise (P1) 'S >= R'        : satisfied {sat_p1}, "
          f"violated {viol_p1}")
    print(f"  premise (P2) 'no R-W edges'  : satisfied {sat_p2}, "
          f"violated {viol_p2}")
    print()
    print("Both premises are contingent over unconstrained finite "
          "structures: their truth for the SPECIFIC objects S, R_{m-1}, "
          "W_m depends entirely on the surrounding construction, which the "
          "claim text does not supply.  The claim quantifies over nothing "
          "enumerable; violating structures above are not counterexamples "
          "to it, and constructing R_{m-1}/W_m ourselves would mean "
          "inventing data the claim does not supply.")
    print()
    print("VERDICT: CLAIM_NOT_FINITELY_REFUTABLE")
    print("WITNESS: none (no finitely checkable predicate is determined by "
          "the claim text alone)")


if __name__ == "__main__":
    main()
