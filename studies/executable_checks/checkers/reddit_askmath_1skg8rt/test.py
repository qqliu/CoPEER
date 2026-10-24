"""For all real x and z, if sin(x)=sin(z), then x=2kπ+z for some integer k."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_askmath_1skg8rt"
WITNESS_DESCRIPTION = "x=0 and z=π: sin(0)=sin(π)=0."
REFUTATION_EXPLANATION = (
    "The required equation would be 0=2kπ+π. Since π is nonzero, "
    "this forces k=-1/2, which is not an integer."
)
SEARCH_SPACE = (
    "All four ordered pairs (x,z)=(aπ,bπ) with a,b in {0,1}, in "
    "lexicographic product order; sin(aπ)=sin(bπ)=0 is checked using the "
    "exact integer-multiple identity, and the conclusion is checked by "
    "whether (a-b)/2 is an integer."
)

witness = None
for a, b in product(range(2), repeat=2):
    premise_holds = True  # Exactly: sin(nπ)=0 for every integer n.
    required_k = Fraction(a - b, 2)
    conclusion_holds = required_k.denominator == 1
    if premise_holds and not conclusion_holds:
        witness = (a, b)
        break

if witness != (0, 1):
    raise AssertionError("the fixed exhaustive sweep did not find its witness")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
