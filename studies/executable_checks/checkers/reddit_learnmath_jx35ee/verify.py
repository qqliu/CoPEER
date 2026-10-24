r"""Method 1 claims that the derivative of e^[(-x)^(2)] is -2e^(-2x)."""

import json


def dual_negate(value):
    return (-value[0], -value[1])


def dual_multiply(left, right):
    return (
        left[0] * right[0],
        left[1] * right[0] + left[0] * right[1],
    )


def dual_scale(value, scalar):
    return (scalar * value[0], scalar * value[1])


def dual_exp_at_zero(value):
    assert value[0] == 0
    return (1, value[1])


witness = 0
variable = (witness, 1)
negative_variable = dual_negate(variable)
inner = dual_multiply(negative_variable, negative_variable)
actual_expression = dual_exp_at_zero(inner)
actual_derivative = actual_expression[1]

claimed_exponent = dual_scale(variable, -2)
claimed_exponential = dual_exp_at_zero(claimed_exponent)
claimed_value = -2 * claimed_exponential[0]

REPORT = {
    "record_id": "reddit_learnmath_jx35ee",
    "verdict": "CONFIRMED",
    "notes": "At x = 0, exact dual-number differentiation gives 0 for the derivative of exp((-x)^2), while the claimed expression evaluates to -2. The refuted derivative identity reflects a substantive differentiation/algebra error, not a plain typo.",
}

assert witness == 0
assert inner == (0, 0)
assert actual_expression == (1, 0)
assert actual_derivative == 0
assert claimed_exponent[0] == 0
assert claimed_exponential[0] == 1
assert claimed_value == -2
assert actual_derivative != claimed_value
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
