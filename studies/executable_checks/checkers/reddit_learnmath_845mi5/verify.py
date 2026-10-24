r'''For a unit-rate Poisson process, the proof incorrectly claims that the probability of exactly one arrival between t and s1 is e^(t-s1), omitting the factor s1-t.'''

import json
from fractions import Fraction
from math import factorial

RECORD_ID = "reddit_learnmath_845mi5"
NOTES = (
    "At t=0 and s1=2, the unit-rate Poisson one-arrival probability is "
    "2e^(-2), while the quoted claim gives e^(-2). Their difference is the "
    "strictly positive quantity e^(-2). The refuted statement is "
    "substantively false, not plainly a typo."
)


def poisson_coefficient(interval_length, arrival_count):
    numerator = interval_length ** arrival_count
    return Fraction(numerator, factorial(arrival_count))


def main():
    t = 0
    s1 = 2
    interval_length = s1 - t
    arrival_count = 1

    correct_coefficient = poisson_coefficient(interval_length, arrival_count)
    claimed_coefficient = Fraction(1, 1)
    correct_exponent = -interval_length
    claimed_exponent = t - s1

    # The alternating series through degree three is an exact positive lower
    # bound for e^(-1); squaring it certifies that e^(-2) is positive.
    exp_minus_one_lower = Fraction(0, 1)
    for n in range(4):
        sign = -1 if n % 2 else 1
        exp_minus_one_lower += Fraction(sign, factorial(n))
    exp_minus_two_lower = exp_minus_one_lower * exp_minus_one_lower

    valid = (
        interval_length > 0
        and correct_exponent == claimed_exponent == -2
        and correct_coefficient == Fraction(2, 1)
        and claimed_coefficient == Fraction(1, 1)
        and correct_coefficient != claimed_coefficient
        and exp_minus_two_lower > 0
    )
    verdict = "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID"
    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": NOTES,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
