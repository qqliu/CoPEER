"""If |x-a|<1 and the sign in 2a±1 is selected according to the sign of x, then |x²-a²|≤|2a±1||x-a|."""

import json
from fractions import Fraction


def main():
    a_candidates = (
        Fraction(-3, 4),
        Fraction(-1, 1),
        Fraction(-1, 2),
        Fraction(0, 1),
        Fraction(1, 2),
        Fraction(1, 1),
    )
    x_candidates = (
        Fraction(1, 10),
        Fraction(-1, 1),
        Fraction(-1, 2),
        Fraction(1, 2),
        Fraction(1, 1),
    )

    violations = []
    for a in a_candidates:
        for x in x_candidates:
            if x == 0 or abs(x - a) >= 1:
                continue
            coefficient = 2 * a + 1 if x > 0 else 2 * a - 1
            left = abs(x * x - a * a)
            right = abs(coefficient) * abs(x - a)
            if left > right:
                violations.append((a, x, left, right))

    expected = (
        Fraction(-3, 4),
        Fraction(1, 10),
        Fraction(221, 400),
        Fraction(17, 40),
    )
    assert violations and violations[0] == expected

    result = {
        "record_id": "reddit_learnmath_1qjwhj",
        "outcome": "WITNESS_FOUND",
        "witness_description": "a=-3/4 and x=1/10, so x>0 selects the + sign in 2a+1 and |x-a|=17/20<1.",
        "refutation_explanation": "For this pair, |x²-a²|=221/400, while |2a+1||x-a|=17/40=170/400. Thus 221/400>170/400, contradicting the claimed ≤ inequality.",
        "search_space": "All 30 ordered pairs (a,x) in A×X were swept, where A=(-3/4,-1,-1/2,0,1/2,1) and X=(1/10,-1,-1/2,1/2,1). Pairs with x≠0 and |x-a|<1 were tested, using + for x>0 and − for x<0.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
