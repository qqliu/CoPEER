"""If ε > 0, a > b, and a < b + ε, then 0 < a < ε."""

import json

record_id = "reddit_askmath_1ok70n5"
witness = None

for epsilon in range(1, 5):
    for a in range(0, 5):
        for b in range(0, 5):
            hypotheses = epsilon > 0 and a > b and a < b + epsilon
            conclusion = 0 < a and a < epsilon
            if hypotheses and not conclusion and witness is None:
                witness = (epsilon, a, b)

assert witness == (2, 2, 1)

result = {
    "record_id": record_id,
    "outcome": "WITNESS_FOUND",
    "witness_description": "ε = 2, a = 2, b = 1.",
    "refutation_explanation": "The hypotheses hold because 2 > 0, 2 > 1, and 2 < 1 + 2. The conclusion 0 < 2 < 2 is false because 2 < 2 is false.",
    "search_space": "All 100 integer triples (ε, a, b) with ε in {1,2,3,4} and a,b in {0,1,2,3,4}, swept completely in lexicographic (ε, a, b) order."
}

print(json.dumps(result, ensure_ascii=False))
