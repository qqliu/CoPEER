r"""For $k = 5$, the RHS is $\frac{ 8 \times 5}{1} > 2 \times 1012$."""

import json
from fractions import Fraction

RECORD_ID = "mse_4710963__ans4710987"
WITNESS_DESCRIPTION = (
    "At k = 5, the stated RHS is (8 * 5) / 1 = 40, while 2 * 1012 = 2024."
)
REFUTATION_EXPLANATION = (
    "The claimed strict inequality is false because 40 is not greater than 2024."
)
SEARCH_SPACE = (
    "The singleton parameter space k in {5}, evaluating (8 * k) / 1 > "
    "2 * 1012 using exact Fraction arithmetic."
)

witness_found = False
for k in (5,):
    rhs = Fraction(8 * k, 1)
    comparison_value = Fraction(2 * 1012, 1)
    if not rhs > comparison_value:
        witness_found = True
        break

assert witness_found
result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
