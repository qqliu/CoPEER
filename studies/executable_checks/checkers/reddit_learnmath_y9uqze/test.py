"""For arbitrary real a and b, {x∈R s.t f'(x)<a} equals {x∈R s.t f(x)<ax+b}."""

import json
from itertools import product

RECORD_ID = "reddit_learnmath_y9uqze"
WITNESS_DESCRIPTION = "f(x)=x^2, a=-2, b=-2, x=-2."
REFUTATION_EXPLANATION = (
    "f'(-2)=-4<-2 is true, but f(-2)=4<(-2)(-2)+(-2)=2 is false, "
    "so x=-2 belongs to the left set and not the right set."
)
SEARCH_SPACE = (
    "All 125 triples (a,b,x) in {-2,-1,0,1,2}^3, for the fixed "
    "differentiable function f(x)=x^2, in lexicographic order."
)

values = range(-2, 3)
first_witness = None
for a, b, x in product(values, values, values):
    derivative_value = 2 * x
    function_value = x * x
    left_membership = derivative_value < a
    right_membership = function_value < a * x + b
    if left_membership != right_membership and first_witness is None:
        first_witness = (a, b, x)

assert first_witness == (-2, -2, -2)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
