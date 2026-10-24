"""The proof asserts the term-by-term identity sum_{p prime} ln(p) * p^{-z}/(1 - p^{-z}) = sum_{p prime} d/dz ln( -1 / (1 - p^{-z}) ). This equality is false: for each prime p the right-hand summand is the NEGATIVE of the left-hand summand, because the constant factor -1 does not change the derivative and d/dz ln(1/(1-p^{-z})) = -ln(p) p^{-z}/(1-p^{-z})."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_31234"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "At p=2 and z=1, writing L=ln(2), the left summand is L while the differentiated right summand is -L; since ln(2) is nonzero, they are unequal."
REFUTATION_EXPLANATION = "Exact symbolic differentiation gives opposite rational coefficients of ln(p): 1/(p**z-1) on the left and -1/(p**z-1) on the right. The bounded sweep checks all 32 specified pairs and selects its first mismatch, p=2 and z=1, where the coefficients are 1 and -1."
SEARCH_SPACE = "All 32 pairs (p,z) where p is one of (2, 3, 5, 7, 11, 13, 17, 19) and z is one of (1, 2, 3, 4), in lexicographic order by p then z."


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return n == divisor
        divisor += 1
    return True


def fraction_div(numerator, denominator):
    if denominator.numerator == 0:
        raise ZeroDivisionError
    return Fraction(
        numerator.numerator * denominator.denominator,
        numerator.denominator * denominator.numerator,
    )


def main():
    primes = tuple(n for n in range(2, 20) if is_prime(n))
    z_values = (1, 2, 3, 4)
    mismatches = []

    for p in primes:
        for z in z_values:
            power = p ** z
            x = Fraction(1, power)
            one_minus_x = Fraction(power - 1, power)

            # Coefficient of ln(p) in x is 0, while in dx/dz it is -x.
            x_prime_coefficient = -x
            left_coefficient = fraction_div(x, one_minus_x)

            # ln(-1/(1-x)) differs locally from -ln(1-x) only by a
            # constant, so its derivative coefficient is
            # -(coefficient of (1-x)' divided by (1-x)).
            right_coefficient = -fraction_div(
                -x_prime_coefficient, one_minus_x
            )

            if left_coefficient != right_coefficient:
                mismatches.append(
                    (p, z, left_coefficient, right_coefficient)
                )

    assert primes == (2, 3, 5, 7, 11, 13, 17, 19)
    assert len(primes) * len(z_values) == 32
    assert len(mismatches) == 32
    assert mismatches[0] == (2, 1, Fraction(1, 1), Fraction(-1, 1))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
