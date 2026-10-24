"""The specialization s=1/n and r=1/(n+1) for an integer n covers arbitrary rational pairs r<s and therefore establishes the universal conclusion."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_h8oug8"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "r=1/4 and s=1/2 are rational and satisfy r<s, but they are not "
    "produced by the stated specialization."
)
REFUTATION_EXPLANATION = (
    "Since s=1/2, the equation s=1/n forces n=2. The specialization "
    "would then require r=1/(n+1)=1/3, contradicting r=1/4. Thus the "
    "specialization does not cover arbitrary rational pairs r<s, so the "
    "claimed universal inference is not established by it."
)
SEARCH_SPACE = (
    "All 55 ordered pairs r<s drawn from the 11 distinct positive fractions "
    "p/q with integers 1<=p<=4 and 1<=q<=4; every pair was checked in "
    "increasing lexicographic order using exact Fraction arithmetic."
)


def is_special_pair(r, s):
    reciprocal_s = Fraction(s.denominator, s.numerator)
    if reciprocal_s.denominator != 1:
        return False
    n = reciprocal_s.numerator
    if n == -1:
        return False
    return r == Fraction(1, n + 1)


def main():
    values = sorted({Fraction(p, q) for p in range(1, 5) for q in range(1, 5)})
    first_witness = None
    checked = 0
    for r in values:
        for s in values:
            if r < s:
                checked += 1
                if not is_special_pair(r, s) and first_witness is None:
                    first_witness = (r, s)

    assert len(values) == 11
    assert checked == 55
    assert first_witness == (Fraction(1, 4), Fraction(1, 2))

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
