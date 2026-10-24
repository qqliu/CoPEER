"""Every injective function f: X -> Y has a left inverse l: Y -> X."""

import itertools
import json


def main():
    first_witness = None

    for m in range(3):
        for n in range(3):
            for f_values in itertools.product(range(n), repeat=m):
                if len(set(f_values)) != m:
                    continue

                has_left_inverse = False
                for l_values in itertools.product(range(m), repeat=n):
                    if all(l_values[f_values[x]] == x for x in range(m)):
                        has_left_inverse = True

                if not has_left_inverse and first_witness is None:
                    first_witness = (m, n, f_values)

    assert first_witness == (0, 1, ())

    result = {
        "record_id": "reddit_learnmath_9i7kh8",
        "outcome": "WITNESS_FOUND",
        "witness_description": "X is the empty set, Y={0}, and f:X->Y is the empty function.",
        "refutation_explanation": "The empty function is injective vacuously, but no function l:Y->X exists because Y is nonempty and X is empty; therefore f has no left inverse.",
        "search_space": "Exhaustively swept canonical finite sets X=range(m) and Y=range(n) for 0<=m,n<=2, every function f:X->Y, and every function l:Y->X as a candidate left inverse, in lexicographic itertools.product order."
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
