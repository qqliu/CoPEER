"""The inference from e1#x = e2#x to e1 = e2 is valid for an arbitrary composition law."""

import itertools
import json

RECORD_ID = "reddit_learnmath_j6piup"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "On the set {0,1}, define a#b = 0 for every ordered pair (a,b). Taking e1=0, e2=1, and x=0 gives e1#x=0=e2#x while e1!=e2."
REFUTATION_EXPLANATION = "The claimed inference requires right cancellation, which an arbitrary composition law need not satisfy. The constant-zero law is a concrete composition law for which the premise is true and the conclusion is false."
SEARCH_SPACE = "All 16 binary operations #:{0,1}x{0,1}->{0,1} and all 8 ordered triples (e1,e2,x) in {0,1}^3 were swept in fixed lexicographic order, for 128 exact checks total."


def main():
    elements = (0, 1)
    witnesses = []
    checks = 0

    # A table's entries correspond, in order, to (0,0), (0,1),
    # (1,0), and (1,1). Product supplies a fixed lexicographic order.
    for table in itertools.product(elements, repeat=4):
        for e1, e2, x in itertools.product(elements, repeat=3):
            checks += 1
            left = table[e1 * 2 + x]
            right = table[e2 * 2 + x]
            if left == right and e1 != e2:
                witnesses.append((table, e1, e2, x))

    assert checks == 128
    expected = ((0, 0, 0, 0), 0, 1, 0)
    assert expected in witnesses

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
