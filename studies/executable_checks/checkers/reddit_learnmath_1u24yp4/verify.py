r"""The conditions b^n ≥ M and x ≥ b suffice to invoke the asymptotic bound x^n/2 ≤ f(x) and conclude f(x) ≥ f(0)."""

import json

RECORD_ID = "reddit_learnmath_1u24yp4"
NOTES = (
    "The witness is valid under exact arithmetic: both stated conditions and "
    "the lower bound hold, while f(1)=1/2<1=f(0). The refuted statement is "
    "substantive, not plainly a typo; it omits the necessary condition "
    "b^n ≥ 2f(0)."
)


def integer_power(base, exponent):
    if exponent < 0:
        raise ValueError("negative exponent")
    result = 1
    factor = base
    remaining = exponent
    while remaining:
        if remaining % 2:
            result *= factor
        factor *= factor
        remaining //= 2
    return result


def rational_le(left, right):
    left_num, left_den = left
    right_num, right_den = right
    if left_den <= 0 or right_den <= 0:
        raise ValueError("denominators must be positive")
    return left_num * right_den <= right_num * left_den


n = 1
b = 1
threshold = 1
x = 1
f_zero = (1, 1)
f_at_x = (1, 2)

b_to_n = integer_power(b, n)
x_to_n = integer_power(x, n)
stated_conditions = b_to_n >= threshold and x >= b
asymptotic_bound = rational_le((x_to_n, 2), f_at_x)
claimed_conclusion = rational_le(f_zero, f_at_x)
missing_condition = b_to_n >= 2 * f_zero[0]

if stated_conditions and asymptotic_bound and not claimed_conclusion and not missing_condition:
    verdict = "CONFIRMED"
else:
    verdict = "REFUTED_WITNESS_INVALID"

result = {
    "record_id": RECORD_ID,
    "verdict": verdict,
    "notes": NOTES,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
