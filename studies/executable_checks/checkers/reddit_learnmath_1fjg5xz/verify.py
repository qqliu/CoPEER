r"""Solution B's unqualified answer -ln(x-1) is an antiderivative of 1/(1-x) on the integrand's real domain, despite requiring x>1."""

import json

RECORD_ID = "reddit_learnmath_1fjg5xz"
NOTES = "Exact recomputation confirms x = 0: 1-x = 1, so the integrand is real-defined, while x-1 = -1 is outside the real logarithm's domain. The refuted statement is substantive, not plainly a typo; the correct real-domain form requires -ln|x-1| (with constants handled separately on the two domain components)."


def main():
    witness = 0
    integrand_denominator = 1 - witness
    logarithm_argument = witness - 1

    integrand_is_real_defined = integrand_denominator != 0
    proposed_expression_is_real_defined = logarithm_argument > 0

    if integrand_is_real_defined and not proposed_expression_is_real_defined:
        verdict = "CONFIRMED"
    else:
        verdict = "REFUTED_WITNESS_INVALID"

    result = {
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
