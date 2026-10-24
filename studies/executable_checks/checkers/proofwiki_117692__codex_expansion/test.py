"""The generalized sum over J converges absolutely to r if and only if the series from n=1 of v_{j_n} converges absolutely to r, although the enumeration begins with j_0."""

import itertools
import json

RECORD_ID = "proofwiki_117692__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let J={j_n:n>=0}, take v_{j_0}=1 and v_{j_n}=0 for every "
    "n>=1, and take r=1."
)
REFUTATION_EXPLANATION = (
    "This family has finite support, so it is absolutely summable. Its "
    "generalized sum over J is 1, hence converges absolutely to r=1. The "
    "series starting at n=1 contains only zero terms and therefore converges "
    "absolutely to 0, not to r=1. Thus the stated equivalence fails because "
    "it omits v_{j_0}."
)
SEARCH_SPACE = (
    "Exhaustively swept all 729 pairs consisting of r in "
    "(1,0,-1,2,-2,3,-3,4,-4) and a family on J={j_n:n>=0} with each of "
    "v_{j_0},...,v_{j_3} in (0,1,-1) and v_{j_n}=0 for every n>=4."
)

values = (0, 1, -1)
r_values = (1, 0, -1, 2, -2, 3, -3, 4, -4)
first_witness = None
examined = 0

for coefficients in itertools.product(values, repeat=4):
    generalized_sum = sum(coefficients)
    series_from_one_sum = sum(coefficients[1:])
    generalized_absolute_mass = sum(abs(value) for value in coefficients)
    series_absolute_mass = sum(abs(value) for value in coefficients[1:])
    assert generalized_absolute_mass >= 0
    assert series_absolute_mass >= 0
    for r in r_values:
        examined += 1
        left_side = generalized_sum == r
        right_side = series_from_one_sum == r
        if left_side != right_side and first_witness is None:
            first_witness = (coefficients, r, generalized_sum, series_from_one_sum)

assert examined == 729
assert first_witness == ((1, 0, 0, 0), 1, 1, 0)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
