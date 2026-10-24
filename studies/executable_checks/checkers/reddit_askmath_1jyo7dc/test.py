"""No fraction with denominator 500 can be equivalent to a fraction with denominator 9, 99, 999, and so on."""

import json


witness = None
for n in range(1, 4):
    denominator = 10 ** n - 1
    for a in range(1, 501):
        for b in range(1, denominator + 1):
            if a * denominator == b * 500 and witness is None:
                witness = (n, a, b)

assert witness == (1, 500, 9)

result = {
    "record_id": "reddit_askmath_1jyo7dc",
    "outcome": "WITNESS_FOUND",
    "witness_description": "The sweep finds a = 500, n = 1, b = 9: 500/500 is equivalent to 9/9.",
    "refutation_explanation": "Both are valid fractions with the specified denominators, and exact cross-multiplication gives 500 * 9 = 9 * 500. Thus the claimed universal non-equivalence is false.",
    "search_space": "All triples (n, a, b) with n in {1, 2, 3}, 1 <= a <= 500, and 1 <= b <= 10^n - 1, tested in fixed nested-loop order using exact integer cross-multiplication."
}
print(json.dumps(result, separators=(",", ":")))
