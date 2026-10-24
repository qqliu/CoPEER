r"""The proposed choice m=(1-3𝜀)/(9𝜀) supplies the natural number required by the sequence-limit definition for every 𝜀>0."""

import json


def gcd_nonnegative(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def main():
    epsilon_numerator = 1
    epsilon_denominator = 1

    if epsilon_numerator <= 0 or epsilon_denominator <= 0:
        raise AssertionError("The witness epsilon must be positive")

    m_numerator = epsilon_denominator - 3 * epsilon_numerator
    m_denominator = 9 * epsilon_numerator
    divisor = gcd_nonnegative(abs(m_numerator), m_denominator)
    reduced_numerator = m_numerator // divisor
    reduced_denominator = m_denominator // divisor

    if reduced_numerator != -2 or reduced_denominator != 9:
        raise AssertionError("Exact witness recomputation failed")

    is_integer = reduced_denominator == 1
    is_natural = is_integer and reduced_numerator >= 0
    if is_natural:
        raise AssertionError("The witness unexpectedly produced a natural number")

    result = {
        "record_id": "reddit_learnmath_9a9ohb",
        "verdict": "CONFIRMED",
        "notes": "The refuted statement is substantive, not plainly a typo: for the positive witness ε=1, the proposed expression is exactly -2/9, which is neither an integer nor a natural number under any standard convention."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
