"""Dividing a = (a * c1) * c2 by a validly yields 1 = c1 * c2 for all integers satisfying the hypotheses."""

import itertools
import json

RECORD_ID = "reddit_askmath_19b1r7e"
VALUES = tuple(range(-10, 11))
WITNESS_DESCRIPTION = "(a, c1, c2) = (0, 0, 0)."
REFUTATION_EXPLANATION = (
    "The supplied equation holds because 0 = (0 * 0) * 0, but dividing by a "
    "would mean dividing by zero, which is invalid, and the asserted conclusion "
    "becomes 1 = 0 * 0 = 0, which is false."
)
SEARCH_SPACE = (
    "All 9,261 integer triples (a, c1, c2) in {-10, -9, ..., 10}^3, "
    "exhaustively checked in lexicographic product order for the supplied "
    "equation and a false asserted conclusion."
)

violations = []
for a, c1, c2 in itertools.product(VALUES, repeat=3):
    supplied_equation_holds = a == (a * c1) * c2
    asserted_conclusion_holds = 1 == c1 * c2
    if supplied_equation_holds and not asserted_conclusion_holds:
        violations.append((a, c1, c2))

witness = (0, 0, 0)
assert witness in violations

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
