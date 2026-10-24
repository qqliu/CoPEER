r'''The final equality |(x-2)(x+2)|/(4x^2) = |x-2||x+2|/(x^2) in line 0013 is valid.'''

import json


def main():
    x = -1

    left_numerator = abs((x - 2) * (x + 2))
    left_denominator = 4 * x * x
    right_numerator = abs(x - 2) * abs(x + 2)
    right_denominator = x * x

    denominators_valid = left_denominator != 0 and right_denominator != 0
    unequal = left_numerator * right_denominator != right_numerator * left_denominator

    if not denominators_valid or not unequal:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The proposed witness does not establish a failure of the stated equality. This prevents classifying the statement as either substantive or plainly a typo."
    else:
        verdict = "CONFIRMED"
        notes = "Exact recomputation at x = -1 gives left = 3/4 and right = 3/1, with both denominators nonzero. Thus the equality fails by a factor of four. This is a substantive algebraic error in the stated equality, not plainly a typo from the permitted evidence."

    result = {
        "record_id": "reddit_learnmath_t6wb5n",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
