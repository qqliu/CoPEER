"""For positive a and b, √(a/b) equals |(a/b)^(-1)|."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_learnmath_1v3cd63"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "a = 1, b = 2: a/b = 1/2, so the left side is √(1/2) "
    "and the right side is 2."
)
REFUTATION_EXPLANATION = (
    "Both sides are positive. If √(1/2) were 2, squaring would give "
    "1/2 = 4, which is false; therefore this positive pair refutes "
    "the universal claim."
)
SEARCH_SPACE = (
    "All 256 ordered pairs (a, b) of positive integers with 1 <= a <= 16 "
    "and 1 <= b <= 16, checked in lexicographic order (a first, then b)."
)

violations = []
for a, b in product(range(1, 17), range(1, 17)):
    ratio = Fraction(a, b)
    right_side = Fraction(b, a)
    # Both quantities are positive, so equality is equivalent to equality
    # after squaring: ratio == right_side * right_side.
    if ratio != right_side * right_side:
        violations.append((a, b))

assert violations
assert violations[0] == (1, 2)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
