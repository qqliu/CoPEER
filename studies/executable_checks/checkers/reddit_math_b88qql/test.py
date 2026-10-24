"""An exact finite presentation over one Noetherian subring passes to the ambient direct-limit ring as an exact presentation of the extended ideal."""

import json

RECORD_ID = "reddit_math_b88qql"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let A be the diagonal copy of Z in R = Z x (Z/2Z), via n |-> "
    "(n, n mod 2). The two-object directed diagram A -> R has colimit R. "
    "For I = 2A, the finite presentation A^0 -> A -> I -> 0, with A -> I "
    "given by multiplication by 2, is exact. Its proposed extension is "
    "R^0 -> R -> 2R -> 0."
)
REFUTATION_EXPLANATION = (
    "The nonzero element e = (0, 1 mod 2) of R lies in the kernel of "
    "multiplication by 2, since 2e = (0, 0 mod 2). Thus R -> 2R is not "
    "injective, so the extended presentation is not exact at R."
)
SEARCH_SPACE = (
    "Exhaustively swept all 196 triples (q,d,b) with 2 <= q <= 8, "
    "2 <= d <= 8, and 1 <= b < q. Each triple denotes R_q = Z x "
    "(Z/qZ), the diagonal subring A = Z, the ideal dA, and the nonzero "
    "element (0,b) tested for annihilation by d. All triples were checked "
    "in lexicographic (q,d,b) order."
)


def exhaustive_search():
    hits = []
    checked = 0
    for q in range(2, 9):
        for d in range(2, 9):
            for b in range(1, q):
                checked += 1
                # In R_q, d * (0,b) = (0, d*b mod q).
                if (d * b) % q == 0:
                    hits.append((q, d, b))
    assert checked == 196
    assert hits
    return hits[0]


def main():
    first = exhaustive_search()
    assert first == (2, 2, 1)
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
