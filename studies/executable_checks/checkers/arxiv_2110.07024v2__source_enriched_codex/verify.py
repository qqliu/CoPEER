r"""In the stated toy model, the cutoff γ_k, distributed as the maximum of c independent Uniform[0,1] variables, has expectation 1−1/c."""

import json
from fractions import Fraction

record_id = "arxiv_2110.07024v2__source_enriched_codex"
verdict = "CONFIRMED"
notes = "Exact recomputation for c=2 gives E[max(U1,U2)]=2/3, while 1−1/c=1/2, a difference of 1/6. The refuted statement is a substantive mathematical error, not plainly a typo."

# By symmetry, integrate max(x, y) over the two triangles of the unit square.
# On 0 <= y <= x <= 1, the inner integral is x*x; its outer integral is 1/3.
def integrate_unit_monomial(coefficient, degree):
    return Fraction(coefficient, degree + 1)

c = 2
triangle_moment = integrate_unit_monomial(1, 2)
actual_expectation = 2 * triangle_moment
claimed_expectation = 1 - Fraction(1, c)
difference = actual_expectation - claimed_expectation

assert actual_expectation == Fraction(2, 3)
assert claimed_expectation == Fraction(1, 2)
assert difference == Fraction(1, 6)
assert actual_expectation != claimed_expectation

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, ensure_ascii=False, separators=(",", ":")))
