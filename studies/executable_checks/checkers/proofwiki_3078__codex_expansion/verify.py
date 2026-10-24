r"""For positive s_i, the proof claims that the derivative with respect to r of (Σ_i s_i^r)^(1/r) equals 0 at r=1."""

import json
from fractions import Fraction

record_id = "proofwiki_3078__codex_expansion"
witness = (1, 1)
point = 1

# For this witness, each term is identically 1 for every real exponent,
# so the function is exactly 2^(1/r).
assert all(entry == 1 for entry in witness)
base = len(witness)
assert base == 2

# If g(r)=1/r, then g'(1)=-1. Differentiating base^g gives
# base^g * log(base) * g'. Thus the following is the exact
# coefficient of log(base) in the derivative at r=1.
reciprocal_derivative = Fraction(-1, point * point)
function_value = base
log_coefficient = function_value * reciprocal_derivative
assert log_coefficient == -2

# From log(base)=integral_1^base (1/x) dx and 1/x >= 1/base on
# [1,base], this exact positive rational is a lower bound for log(base).
log_lower_bound = Fraction(base - 1, base)
assert log_lower_bound > 0

derivative_is_nonzero = log_coefficient != 0 and log_lower_bound > 0
verdict = "CONFIRMED" if derivative_is_nonzero else "REFUTED_WITNESS_INVALID"
notes = (
    "Independent exact recomputation gives the derivative for (1,1) as "
    "-2*log(2). Since log(2) is strictly positive, the derivative is nonzero. "
    "The refuted statement is substantive, not plainly a typo."
)

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
