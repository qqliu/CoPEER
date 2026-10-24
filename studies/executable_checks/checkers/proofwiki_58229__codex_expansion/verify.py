r"""For the substitution t = π(x-a)/(b-a), the normalization integral equals π/(b-a) times the corresponding integral over [0,π]."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_58229__codex_expansion"
NOTES = (
    "Exact recomputation confirms the witness: the Jacobian gives an actual "
    "value of 1/2, while the claimed expression is π²/2 and is strictly "
    "larger. This is a substantive normalization error, not a plainly "
    "identifiable typo."
)


def multiply_pi_monomials(left, right):
    return left[0] * right[0], left[1] + right[1]


def sine_at_integer_multiple_of_pi(multiplier):
    if not isinstance(multiplier, int):
        raise TypeError("integer multiplier required")
    return 0


# Concrete witness and exact endpoint mapping.
a = 0
b = 1
length = b - a
mapped_a = Fraction(a - a, length)
mapped_b = Fraction(b - a, length)

# From sin²(t) = (1-cos(2t))/2, an antiderivative is
# t/2 - sin(2t)/4. Both boundary sine terms vanish exactly.
boundary_term = Fraction(
    sine_at_integer_multiple_of_pi(2)
    - sine_at_integer_multiple_of_pi(0),
    4,
)
corresponding_integral = (Fraction(1, 2), 1)  # (coefficient, power of π)

# dx = length/π dt, whereas the claim uses π/length.
jacobian = (Fraction(length, 1), -1)
claimed_factor = (Fraction(1, length), 1)
actual_integral = multiply_pi_monomials(jacobian, corresponding_integral)
claimed_integral = multiply_pi_monomials(claimed_factor, corresponding_integral)

# The first two Gregory-series terms give the strict exact bound
# π/4 > 1 - 1/3, hence π > 8/3.
quarter_pi_lower_bound = Fraction(1, 1) - Fraction(1, 3)
pi_lower_bound = 4 * quarter_pi_lower_bound
claimed_lower_bound = (
    claimed_integral[0] * pi_lower_bound * pi_lower_bound
)

verified = (
    mapped_a == 0
    and mapped_b == 1
    and boundary_term == 0
    and actual_integral == (Fraction(1, 2), 0)
    and claimed_integral == (Fraction(1, 2), 2)
    and pi_lower_bound > 0
    and claimed_lower_bound > actual_integral[0]
)
if not verified:
    raise RuntimeError("exact witness verification failed")

result = {
    "record_id": RECORD_ID,
    "verdict": "CONFIRMED",
    "notes": NOTES,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
