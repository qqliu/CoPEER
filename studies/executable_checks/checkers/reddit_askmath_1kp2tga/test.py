"""The stated closed-form formula solves the recurrence with the initial condition s_0 = 0."""

import json


def multiply(left, right):
    a, b = left
    c, d = right
    return (a * c + 3 * b * d, a * d + b * c)


def exact_power(base, exponent):
    result = (1, 0)
    for _ in range(exponent):
        result = multiply(result, base)
    return result


x = (2, 1)
y = (2, -1)
witness = None

for i in range(1):
    exponent = 2 ** i
    x_term = exact_power(x, exponent)
    y_term = exact_power(y, exponent)
    value = (x_term[0] + y_term[0], x_term[1] + y_term[1])
    if i == 0 and value != (0, 0):
        witness = (i, value)
        break

assert witness == (0, (4, 0))

result = {
    "record_id": "reddit_askmath_1kp2tga",
    "outcome": "WITNESS_FOUND",
    "witness_description": "At i = 0, the stated formula yields s_0 = 4.",
    "refutation_explanation": "Exactly, 2^0 = 1, so s_0 = (2 + sqrt(3)) + (2 - sqrt(3)) = 4, which is not the required initial value 0. Thus the formula violates the stated initial condition, independently of the unspecified recurrence.",
    "search_space": "The single required initial-condition index i in {0}, evaluated exactly in Z[sqrt(3)] with sqrt(3) represented by coefficient pairs and the relation (sqrt(3))^2 = 3."
}

print(json.dumps(result))
