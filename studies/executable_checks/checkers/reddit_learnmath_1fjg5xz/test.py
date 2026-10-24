"""Solution B's unqualified answer -ln(x-1) is an antiderivative of 1/(1-x) on the integrand's real domain, despite requiring x>1."""

import json


def main():
    points = tuple(range(0, 3))
    witnesses = []

    for x in points:
        integrand_is_real_defined = (1 - x) != 0
        proposed_log_is_real_defined = (x - 1) > 0
        if integrand_is_real_defined and not proposed_log_is_real_defined:
            witnesses.append(x)

    if witnesses:
        x = witnesses[0]
        assert x == 0
        result = {
            "record_id": "reddit_learnmath_1fjg5xz",
            "outcome": "WITNESS_FOUND",
            "witness_description": "x = 0. The integrand 1/(1-x) is real and defined there because 1-0 = 1 is nonzero, but -ln(x-1) would require the real logarithm of -1, which is undefined.",
            "refutation_explanation": "An antiderivative asserted on the integrand's entire real domain must itself be real-defined throughout that domain. At x = 0 the integrand is defined, while the proposed expression -ln(x-1) is not real-defined. Thus the unqualified answer cannot be an antiderivative on the integrand's full real domain.",
            "search_space": "All integers x in {0, 1, 2}, checked in increasing order; the complete three-point space was swept using the exact conditions 1-x != 0 for the integrand and x-1 > 0 for the proposed real logarithm."
        }
    else:
        result = {
            "record_id": "reddit_learnmath_1fjg5xz",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No witness was found.",
            "refutation_explanation": "The bounded search found no domain mismatch.",
            "search_space": "All integers x in {0, 1, 2}, checked in increasing order."
        }

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
