"""For every vector space over an infinite field, every vector v satisfying v = -v must satisfy v = 0."""

import json

RECORD_ID = "proofwiki_27030__codex_expansion"
CONFIRMED_NOTE = (
    "The statement is substantively false, not a typo: over the infinite "
    "characteristic-2 field F_2(t), the nonzero vector v=1 satisfies v=-v."
)


def f2_add(a, b):
    return (a + b) % 2


def f2_mul(a, b):
    return (a * b) % 2


def f2_neg(a):
    return (-a) % 2


def f2_is_field():
    elements = (0, 1)
    for a in elements:
        if f2_add(a, 0) != a or f2_mul(a, 1) != a:
            return False
        if f2_add(a, f2_neg(a)) != 0:
            return False
        if a != 0 and f2_mul(a, a) != 1:
            return False
        for b in elements:
            if f2_add(a, b) != f2_add(b, a):
                return False
            if f2_mul(a, b) != f2_mul(b, a):
                return False
            for c in elements:
                if f2_add(f2_add(a, b), c) != f2_add(a, f2_add(b, c)):
                    return False
                if f2_mul(f2_mul(a, b), c) != f2_mul(a, f2_mul(b, c)):
                    return False
                if f2_mul(a, f2_add(b, c)) != f2_add(f2_mul(a, b), f2_mul(a, c)):
                    return False
    return True


# A polynomial over F_2 is encoded by an integer whose bit n is the
# coefficient of t^n. Polynomial multiplication is carryless multiplication.
def poly_mul(left, right):
    product = 0
    position = 0
    remaining = right
    while remaining:
        if remaining & 1:
            product ^= left << position
        remaining >>= 1
        position += 1
    return product


def poly_neg(poly):
    result = 0
    position = 0
    remaining = poly
    while remaining:
        coefficient = remaining & 1
        result |= f2_neg(coefficient) << position
        remaining >>= 1
        position += 1
    return result


def monomial(exponent):
    if not isinstance(exponent, int) or exponent < 0:
        raise ValueError("the exponent must be a nonnegative integer")
    return 1 << exponent


def monomial_degree(exponent):
    return monomial(exponent).bit_length() - 1


def monomial_injection_check(left_exponent, right_exponent):
    left = monomial(left_exponent)
    right = monomial(right_exponent)
    return (left == right) == (left_exponent == right_exponent)


# Fractions (numerator, denominator) represent elements of F_2(t).
def rational_equal(left, right):
    left_num, left_den = left
    right_num, right_den = right
    if left_den == 0 or right_den == 0:
        return False
    return poly_mul(left_num, right_den) == poly_mul(right_num, left_den)


def rational_neg(value):
    numerator, denominator = value
    return (poly_neg(numerator), denominator)


def verify():
    if not f2_is_field():
        return False

    # The bit encodings of t^n have degree n. Hence n -> t^n is an
    # injection from all nonnegative integers into F_2(t), proving infinity.
    degree_checks = all(monomial_degree(n) == n for n in (0, 1, 2, 8, 31))
    separation_checks = all(
        monomial_injection_check(a, b)
        for a, b in ((0, 0), (0, 1), (2, 9), (17, 3), (31, 31))
    )
    if not degree_checks or not separation_checks:
        return False

    zero_vector = (0, 1)
    witness_vector = (1, 1)
    characteristic_two = f2_add(1, 1) == 0
    fixed_by_negation = rational_equal(witness_vector, rational_neg(witness_vector))
    nonzero = not rational_equal(witness_vector, zero_vector)
    return characteristic_two and fixed_by_negation and nonzero


def main():
    valid = verify()
    verdict = "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID"
    notes = CONFIRMED_NOTE if valid else (
        "The proposed substantive counterexample could not be validated exactly."
    )
    result = {"record_id": RECORD_ID, "verdict": verdict, "notes": notes}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
