r"""{4 \choose 2} \cdot \left( \frac{1}{2} \right)^{2^{d-1}} = \frac{6}{2^{2^{d-1}}} < 1, \text{ for $d>1$.}"""

import json
from fractions import Fraction
from math import comb

RECORD_ID = "SE_math_3804372__q"
WITNESS_DESCRIPTION = "d=2 is a concrete witness: 2>1 and both displayed expressions equal 3/2."
REFUTATION_EXPLANATION = (
    "For d=2, 2^(d-1)=2, so C(4,2)*(1/2)^2=6/4=3/2 and "
    "6/2^2=3/2. Since 3/2 is not less than 1, the claimed strict inequality fails."
)
SEARCH_SPACE = (
    "All integer d in the inclusive range 2 through 16 were tested in increasing "
    "order using exact Fraction arithmetic."
)

violations = []
for d in range(2, 17):
    exponent = 2 ** (d - 1)
    left = comb(4, 2) * (Fraction(1, 2) ** exponent)
    right = Fraction(6, 2 ** exponent)
    if left != right or not (right < 1):
        violations.append((d, left, right))

expected = (2, Fraction(3, 2), Fraction(3, 2))
if not violations or violations[0] != expected:
    raise AssertionError("deterministic exact search did not find the expected witness")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
