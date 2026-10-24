r'''The inductive-step equality 5^(k+1) − 2^(k+1) = 3^(k+1) holds.'''

import json


def exact_power(base, exponent):
    if not isinstance(exponent, int) or exponent < 0:
        raise ValueError("exponent must be a nonnegative integer")
    result = 1
    factor = base
    remaining = exponent
    while remaining:
        if remaining % 2:
            result *= factor
        factor *= factor
        remaining //= 2
    return result


def main():
    k = 1
    exponent = k + 1
    left = exact_power(5, exponent) - exact_power(2, exponent)
    right = exact_power(3, exponent)

    if left == 21 and right == 9 and left != right:
        verdict = "CONFIRMED"
        notes = "Exact recomputation at the valid integer witness k = 1 gives 5^(k+1) - 2^(k+1) = 21 and 3^(k+1) = 9, so the equality fails. The refuted statement is substantive, not plainly a typo."
    else:
        verdict = "CANNOT_REPRODUCE"
        notes = "Exact recomputation did not reproduce the reported witness. The refuted statement is substantive, not plainly a typo."

    print(json.dumps({
        "record_id": "reddit_askmath_g7lcfx",
        "verdict": verdict,
        "notes": notes
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
