r"""The proof asserts the term-by-term identity sum_{p prime} ln(p) * p^{-z}/(1 - p^{-z}) = sum_{p prime} d/dz ln( -1 / (1 - p^{-z}) ). This equality is false: for each prime p the right-hand summand is the NEGATIVE of the left-hand summand, because the constant factor -1 does not change the derivative and d/dz ln(1/(1-p^{-z})) = -ln(p) p^{-z}/(1-p^{-z})."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_31234"
VERDICT = "CONFIRMED"
NOTES = ("At p=2 and z=1, exact differentiation gives coefficients 1 and -1 "
         "multiplying ln(2). Since ln(2)>0, the summands differ. A local "
         "complex logarithm exists at the nonzero argument -2, and its branch "
         "choice does not affect the derivative. This is a substantive sign "
         "error, not plainly a typo.")


def main():
    p = 2
    z = 1

    is_prime = p >= 2 and all(p % divisor != 0 for divisor in range(2, p))
    assert is_prime
    assert z >= 0

    scale = 1
    for _ in range(z):
        scale *= p
    assert scale == 2

    # For t=p^(-z), the left coefficient of ln(p) is t/(1-t).
    left_coefficient = Fraction(1, scale - 1)

    # The coefficient of ln(p) in dt/dz is -t.  For
    # g=-1/(1-t), the logarithmic derivative g'/g equals t'/(1-t).
    t_prime_coefficient = Fraction(-1, scale)
    right_coefficient = Fraction(
        t_prime_coefficient.numerator * scale,
        t_prime_coefficient.denominator * (scale - 1),
    )

    log_argument = Fraction(-scale, scale - 1)
    log_lower_bound = Fraction(p - 1, p)

    assert log_argument == Fraction(-2, 1)
    assert log_argument != 0
    assert log_lower_bound > 0
    assert left_coefficient == Fraction(1, 1)
    assert right_coefficient == Fraction(-1, 1)
    assert left_coefficient != right_coefficient

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
