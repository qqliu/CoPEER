"""The rewrite (0^m)(0^(-m)) = 0^(m-m) validly applies the exponent law at base 0."""

import json


def zero_power(exponent):
    """Return (defined, value) for 0 raised to an integer exponent."""
    if exponent < 0:
        return False, None
    if exponent == 0:
        return True, 1
    return True, 0


def main():
    witnesses = []

    for m in range(1, 2):
        positive_defined, positive_value = zero_power(m)
        negative_defined, negative_value = zero_power(-m)
        rhs_defined, rhs_value = zero_power(m - m)

        if not (positive_defined and negative_defined):
            witnesses.append(m)
        elif not rhs_defined or positive_value * negative_value != rhs_value:
            witnesses.append(m)

    assert witnesses == [1]

    result = {
        "record_id": "reddit_askmath_cidcul",
        "outcome": "WITNESS_FOUND",
        "witness_description": "m = 1: 0^1 is 0, but 0^(-1) is undefined because it would require the reciprocal of 0.",
        "refutation_explanation": "Thus (0^1)(0^(-1)) is undefined, so it cannot validly be rewritten as 0^(1-1) = 0^0; the exponent law is not applicable at base 0 for this instance.",
        "search_space": "All integer m with 1 <= m <= 1 (the singleton {1}), tested in increasing order under the standard integer-exponent definition.",
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
