r"""The rewrite (0^m)(0^(-m)) = 0^(m-m) validly applies the exponent law at base 0."""

import json


def nonnegative_power(base, exponent):
    assert isinstance(exponent, int) and exponent >= 0
    result = 1
    remaining = exponent
    while remaining:
        result *= base
        remaining -= 1
    return result


def integer_power_as_ratio(base, exponent):
    if exponent >= 0:
        return True, nonnegative_power(base, exponent), 1
    denominator = nonnegative_power(base, -exponent)
    if denominator == 0:
        return False, None, None
    return True, 1, denominator


def main():
    m = 1
    left_positive = integer_power_as_ratio(0, m)
    left_negative = integer_power_as_ratio(0, -m)
    combined_exponent = m + (-m)
    right = integer_power_as_ratio(0, combined_exponent)

    assert left_positive == (True, 0, 1)
    assert left_negative == (False, None, None)
    assert combined_exponent == 0
    assert right == (True, 1, 1)

    rewrite_fails = left_positive[0] and not left_negative[0] and right[0]
    assert rewrite_fails

    result = {
        "record_id": "reddit_askmath_cidcul",
        "verdict": "CONFIRMED",
        "notes": "Exact integer-exponent recomputation at m = 1 shows that 0^1 is defined as 0 while 0^(-1) is undefined, since its reciprocal denominator is 0; therefore the product and the proposed rewrite are invalid. This is a substantive domain error, not a plain typo.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
