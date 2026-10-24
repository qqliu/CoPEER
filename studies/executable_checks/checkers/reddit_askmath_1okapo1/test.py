"""Dividing both sides by x is valid without imposing the precondition x ≠ 0."""

import json

witnesses = []
for x in range(-10, 11):
    left_side = x * x + 2 * x + 1
    right_side = 1
    equation_holds = left_side == right_side
    division_by_x_is_defined = x != 0
    if equation_holds and not division_by_x_is_defined:
        witnesses.append(x)

if witnesses:
    result = {
        "record_id": "reddit_askmath_1okapo1",
        "outcome": "WITNESS_FOUND",
        "witness_description": "x = 0 is a witness: the supplied equation becomes 1 = 1, while division by x would be division by zero.",
        "refutation_explanation": "At x = 0, x² + 2x + 1 = 1 is true, but dividing either side by x is undefined. Therefore the division step is not valid unless x ≠ 0 is imposed.",
        "search_space": "All 21 integers x from -10 through 10 inclusive, swept in ascending order; each was tested for the supplied equality and whether division by x is defined.",
    }
else:
    result = {
        "record_id": "reddit_askmath_1okapo1",
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "No witness was found in the bounded integer space.",
        "refutation_explanation": "The bounded search found no integer satisfying the equation for which division by x is undefined.",
        "search_space": "All 21 integers x from -10 through 10 inclusive, swept in ascending order; each was tested for the supplied equality and whether division by x is defined.",
    }

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
