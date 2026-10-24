r'''For every nonzero real number a and every nonnegative integer n, a^n = 1.'''

import json


def integer_power(base, exponent):
    if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
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
    candidate_a = -2
    candidate_n = 1
    value = integer_power(candidate_a, candidate_n)
    valid_domain = (
        isinstance(candidate_a, int)
        and not isinstance(candidate_a, bool)
        and candidate_a != 0
        and isinstance(candidate_n, int)
        and not isinstance(candidate_n, bool)
        and candidate_n >= 0
    )
    disproves_claim = valid_domain and value != 1
    if disproves_claim:
        verdict = "CONFIRMED"
        notes = "Exact integer arithmetic verifies that a = -2 is a nonzero real number, n = 1 is a nonnegative integer, and (-2)^1 = -2 != 1. The refuted statement is substantive, not plainly a typo."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The proposed witness does not refute the claim. The refuted statement is substantive, not plainly a typo."
    print(json.dumps({"record_id": "reddit_learnmath_4vn5qm", "verdict": verdict, "notes": notes}))


if __name__ == "__main__":
    main()
