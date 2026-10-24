"""The proof asserts that (1+2/(k-1))^(a-1) is at most 1+2(a-1)/(k-1), an inequality used to establish Part 1's upper bound in the Non-Intersection Bias Lemma."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "arxiv_1304.1796v2__source_enriched_codex"
A_VALUES = (1, 2, 3)
K_VALUES = (2, 3, 4, 5, 10, 100, 1000, 1000001)

violations = []
for a, k in product(A_VALUES, K_VALUES):
    left = (Fraction(1, 1) + Fraction(2, k - 1)) ** (a - 1)
    right = Fraction(1, 1) + Fraction(2 * (a - 1), k - 1)
    if left > right:
        violations.append((a, k, left, right))

witness = max(violations, key=lambda item: (item[1], -item[0]))
assert witness == (
    3,
    1000001,
    Fraction(250001000001, 250000000000),
    Fraction(250001000000, 250000000000),
)
assert witness[2] - witness[3] == Fraction(1, 250000000000)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": "At a=3 and k=1000001, the left side is 250001000001/250000000000, while the asserted upper bound is 250001000000/250000000000.",
    "refutation_explanation": "The left side exceeds the claimed upper bound by exactly 1/250000000000, so the asserted at-most inequality is false for this concrete integer pair.",
    "search_space": "The complete 24-pair Cartesian product a in (1, 2, 3) and k in (2, 3, 4, 5, 10, 100, 1000, 1000001) was evaluated in fixed tuple order using Fraction arithmetic.",
}
print(json.dumps(result, separators=(",", ":")))
