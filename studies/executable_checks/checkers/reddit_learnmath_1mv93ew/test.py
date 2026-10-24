"""The polynomial L^(n+1)-2L^n+1=0 has a unique positive real solution that determines the ratio."""

import json
from fractions import Fraction


def polynomial(n, value):
    return value ** (n + 1) - 2 * value ** n + 1


candidate_ns = (1, 2)
candidate_intervals = ((Fraction(3, 2), Fraction(2, 1)),)
certificates = []

for n in candidate_ns:
    for left, right in candidate_intervals:
        value_at_one = polynomial(n, Fraction(1, 1))
        value_at_left = polynomial(n, left)
        value_at_right = polynomial(n, right)
        if (
            value_at_one == 0
            and Fraction(1, 1) < left < right
            and value_at_left * value_at_right < 0
        ):
            certificates.append((n, left, right, value_at_left, value_at_right))

assert certificates == [
    (2, Fraction(3, 2), Fraction(2, 1), Fraction(-1, 8), Fraction(1, 1))
]

result = {
    "record_id": "reddit_learnmath_1mv93ew",
    "outcome": "WITNESS_FOUND",
    "witness_description": "For n=2, the polynomial has the two distinct positive solutions L=1 and L=(1+sqrt(5))/2.",
    "refutation_explanation": "At n=2 the polynomial is L^3-2L^2+1=(L-1)(L^2-L-1). Thus L=1 is a positive root, while (1+sqrt(5))/2 is another positive root. The exact search also certifies the latter root without numerical approximation: the polynomial equals -1/8 at L=3/2 and 1 at L=2, so continuity gives a root in (3/2,2), which cannot equal 1. Hence the asserted uniqueness fails.",
    "search_space": "Exhaustively swept all pairs (n,(a,b)) with n in {1,2} and (a,b) in {(3/2,2)}, checking exactly that L=1 is a root and that opposite endpoint signs certify a distinct positive root in (a,b).",
}

print(json.dumps(result, separators=(",", ":")))
