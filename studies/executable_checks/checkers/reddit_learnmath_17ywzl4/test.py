"""The inequalities b − ε < q < b with q rational imply q ∈ T = ℚ ∩ [a,b]."""

import json
from fractions import Fraction
from itertools import product

A_VALUES = (Fraction(0, 1),)
B_VALUES = (Fraction(1, 1),)
EPSILON_VALUES = (Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
Q_VALUES = (
    Fraction(-2, 1),
    Fraction(-1, 1),
    Fraction(-1, 2),
    Fraction(0, 1),
    Fraction(1, 2),
    Fraction(1, 1),
    Fraction(2, 1),
)

witnesses = []
for a, b, epsilon, q in product(
    A_VALUES, B_VALUES, EPSILON_VALUES, Q_VALUES
):
    antecedent = b - epsilon < q < b
    in_t = a <= q <= b
    if antecedent and not in_t:
        witnesses.append((a, b, epsilon, q))

expected = (Fraction(0, 1), Fraction(1, 1), Fraction(2, 1), Fraction(-1, 2))
assert witnesses
assert witnesses[0] == expected

result = {
    "record_id": "reddit_learnmath_17ywzl4",
    "outcome": "WITNESS_FOUND",
    "witness_description": "a=0, b=1, ε=2, q=-1/2.",
    "refutation_explanation": (
        "Here q is rational and b−ε=-1 < -1/2 < 1=b, but q=-1/2 is not "
        "in ℚ ∩ [0,1]. Thus the stated inequalities do not imply q ∈ T."
    ),
    "search_space": (
        "Exhaustively swept all 21 tuples in {0} × {1} × {1/2,1,2} × "
        "{-2,-1,-1/2,0,1/2,1,2}, in that fixed order, using exact Fraction "
        "arithmetic."
    ),
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
