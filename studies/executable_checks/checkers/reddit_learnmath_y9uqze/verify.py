r"""For arbitrary real a and b, {x∈R s.t f'(x)<a} equals {x∈R s.t f(x)<ax+b}."""

import json

REPORT = {
    "record_id": "reddit_learnmath_y9uqze",
    "verdict": "CONFIRMED",
    "notes": "Exact integer recomputation verifies the witness: for f(x)=x^2 at a=b=x=-2, f'(x)=-4<-2 while f(x)=4 is not <2. The refuted statement is substantive, not plainly a typo.",
}


def evaluate_polynomial(coefficients, argument):
    value = 0
    monomial = 1
    for coefficient in coefficients:
        value += coefficient * monomial
        monomial *= argument
    return value


def derivative_coefficients(coefficients):
    return tuple(
        degree * coefficients[degree]
        for degree in range(1, len(coefficients))
    )


f_coefficients = (0, 0, 1)
f_prime_coefficients = derivative_coefficients(f_coefficients)
a = -2
b = -2
x = -2

assert f_prime_coefficients == (0, 2)
assert evaluate_polynomial(f_coefficients, x) == 4
assert evaluate_polynomial(f_prime_coefficients, x) == -4
assert a * x + b == 2

left_membership = evaluate_polynomial(f_prime_coefficients, x) < a
right_membership = evaluate_polynomial(f_coefficients, x) < a * x + b
assert left_membership
assert not right_membership
assert left_membership != right_membership
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
