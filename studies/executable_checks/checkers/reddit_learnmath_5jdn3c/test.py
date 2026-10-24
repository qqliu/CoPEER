"""If ab ≡ 0 (mod m) and a,b are nonzero integers, then a has no inverse modulo m."""

import json


RECORD_ID = "reddit_learnmath_5jdn3c"
WITNESS_DESCRIPTION = "m=2, a=1, b=2, with inverse x=1."
REFUTATION_EXPLANATION = (
    "Both a and b are nonzero, and a*b=2 is congruent to 0 modulo 2. "
    "Nevertheless, x=1 is an inverse of a=1 modulo 2 because a*x=1 "
    "is congruent to 1 modulo 2."
)
SEARCH_SPACE = (
    "All 350 quadruples (m,a,b,x) with m in {2,3,4,5}, a and b in "
    "{1,2,3,4,5}, and x in {0,...,m-1}, checked in increasing "
    "lexicographic loop order."
)


def main():
    first_witness = None
    checked = 0

    for m in range(2, 6):
        for a in range(1, 6):
            for b in range(1, 6):
                for x in range(m):
                    checked += 1
                    hypotheses_hold = a != 0 and b != 0 and (a * b) % m == 0
                    inverse_exists = (a * x) % m == 1
                    if hypotheses_hold and inverse_exists and first_witness is None:
                        first_witness = (m, a, b, x)

    assert checked == 350
    assert first_witness == (2, 1, 2, 1)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
