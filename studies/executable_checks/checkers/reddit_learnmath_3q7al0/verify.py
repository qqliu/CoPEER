r"""The submitted proof claims that 2/3 + 1 = 1."""

import json


def main():
    first_numerator = 2
    first_denominator = 3
    second_numerator = 1
    second_denominator = 1
    asserted_numerator = 1
    asserted_denominator = 1

    sum_numerator = (
        first_numerator * second_denominator
        + second_numerator * first_denominator
    )
    sum_denominator = first_denominator * second_denominator

    reported_value_is_reproduced = (
        sum_numerator * 3 == 5 * sum_denominator
    )
    asserted_equality_is_false = (
        sum_numerator * asserted_denominator
        != asserted_numerator * sum_denominator
    )

    if reported_value_is_reproduced and asserted_equality_is_false:
        verdict = "CONFIRMED"
        notes = "Independent exact integer cross-multiplication confirms that 2/3 + 1 = 5/3, and 5/3 is not 1. The refuted equality is plainly an arithmetic typo rather than a substantive mathematical statement."
    else:
        verdict = "CANNOT_REPRODUCE"
        notes = "Independent exact arithmetic did not reproduce the reported witness. The refuted equality appears intended as a plainly arithmetic typo rather than a substantive mathematical statement."

    result = {
        "record_id": "reddit_learnmath_3q7al0",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
