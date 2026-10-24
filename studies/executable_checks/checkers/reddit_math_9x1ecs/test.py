"""The formula sgn(x) = (abs(x)-x)/x + 1 defines the sign of a number without excluding zero."""

import json

CANDIDATES = (0,)
undefined_inputs = []

for x in CANDIDATES:
    numerator = abs(x) - x
    denominator = x
    if denominator == 0:
        undefined_inputs.append((x, numerator))

assert undefined_inputs == [(0, 0)]

result = {
    "record_id": "reddit_math_9x1ecs",
    "outcome": "WITNESS_FOUND",
    "witness_description": "x = 0.",
    "refutation_explanation": "At x = 0, the formula contains division by x, hence division by zero, so it is undefined at zero and cannot define the sign without excluding zero.",
    "search_space": "Exactly the singleton integer set {0}; its sole element was checked.",
}

print(json.dumps(result, separators=(",", ":")))
