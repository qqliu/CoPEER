"""If x<y and a<=b, then a*x<b*y always holds."""

import itertools
import json

values = tuple(range(-2, 3))
first_witness = None
total_count = 0
premise_count = 0

for x, y, a, b in itertools.product(values, repeat=4):
    total_count += 1
    if x < y and a <= b:
        premise_count += 1
        if not (a * x < b * y) and first_witness is None:
            first_witness = (x, y, a, b)

assert total_count == 625
assert premise_count == 150
assert first_witness == (-2, -1, -2, -2)

result = {
    "record_id": "reddit_askmath_q8lalm",
    "outcome": "WITNESS_FOUND",
    "witness_description": "x=-2, y=-1, a=-2, b=-2.",
    "refutation_explanation": "The premises hold because -2 < -1 and -2 <= -2, but a*x = 4 and b*y = 2, so a*x < b*y is false.",
    "search_space": "All 625 integer quadruples (x,y,a,b) in {-2,-1,0,1,2}^4 were swept in lexicographic product order; all 150 quadruples satisfying x<y and a<=b were tested."
}

print(json.dumps(result, separators=(",", ":")))
