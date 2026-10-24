"""For every vector space over an infinite field, every vector v satisfying v = -v must satisfy v = 0."""

import json


PRIMES = (2, 3, 5, 7)
WITNESS_DESCRIPTION = (
    "Let K = F_2(t), the rational-function field over the two-element field, "
    "let V = K as a one-dimensional K-vector space, and take v = 1."
)
REFUTATION_EXPLANATION = (
    "K is infinite because 1, t, t^2, ... are pairwise distinct. Its "
    "characteristic is 2, so -1 = 1; hence v = -v while v != 0. Thus the "
    "universal claim is false, and the source quote's inference that an "
    "infinite field has characteristic 0 fails."
)
SEARCH_SPACE = (
    "All 17 constant-coordinate vectors a in the one-dimensional spaces "
    "V = F_p(t), for p in (2, 3, 5, 7) and a in {0, ..., p-1}, iterated in "
    "increasing p and then increasing a."
)


def canonical_polynomial(coefficients, p):
    result = tuple(coefficient % p for coefficient in coefficients)
    while result and result[-1] == 0:
        result = result[:-1]
    return result


def multiply_polynomials(left, right, p):
    if not left or not right:
        return ()
    coefficients = [0] * (len(left) + len(right) - 1)
    for left_index, left_coefficient in enumerate(left):
        for right_index, right_coefficient in enumerate(right):
            position = left_index + right_index
            coefficients[position] = (
                coefficients[position] + left_coefficient * right_coefficient
            ) % p
    return canonical_polynomial(coefficients, p)


def constant_rational_function(value, p):
    return (canonical_polynomial((value,), p), (1,), p)


def negate_rational_function(value):
    numerator, denominator, p = value
    negated = canonical_polynomial(tuple(-coefficient for coefficient in numerator), p)
    return (negated, denominator, p)


def equal_rational_functions(left, right):
    left_numerator, left_denominator, left_p = left
    right_numerator, right_denominator, right_p = right
    if left_p != right_p:
        return False
    return multiply_polynomials(left_numerator, right_denominator, left_p) == multiply_polynomials(
        right_numerator, left_denominator, left_p
    )


def is_zero_rational_function(value):
    numerator, _denominator, _p = value
    return not numerator


def is_prime(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


def main():
    witnesses = []
    examined = 0
    for p in PRIMES:
        if not is_prime(p):
            continue
        # F_p(t) is infinite: its monomials t^n have distinct degrees.
        for scalar in range(p):
            examined += 1
            vector = constant_rational_function(scalar, p)
            if equal_rational_functions(vector, negate_rational_function(vector)) and not is_zero_rational_function(vector):
                witnesses.append((p, scalar))

    if examined == 17 and witnesses and witnesses[0] == (2, 1):
        outcome = "WITNESS_FOUND"
        witness_description = WITNESS_DESCRIPTION
        refutation_explanation = REFUTATION_EXPLANATION
    else:
        outcome = "NO_WITNESS_INCONCLUSIVE"
        witness_description = "No validated witness was produced."
        refutation_explanation = "The bounded construction search did not produce its expected result."

    result = {
        "record_id": "proofwiki_27030__codex_expansion",
        "outcome": outcome,
        "witness_description": witness_description,
        "refutation_explanation": refutation_explanation,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
