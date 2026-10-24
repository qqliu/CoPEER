r"""If ab ≡ 0 (mod m) and a,b are nonzero integers, then a has no inverse modulo m."""

import json


def is_congruent(left, right, modulus):
    quotient, remainder = divmod(left - right, modulus)
    return quotient * modulus + remainder == left - right and remainder == 0


def main():
    modulus = 2
    a = 1
    b = 2
    inverse = 1

    hypotheses_hold = (
        modulus > 1
        and a != 0
        and b != 0
        and is_congruent(a * b, 0, modulus)
    )
    a_has_reported_inverse = is_congruent(a * inverse, 1, modulus)
    confirmed = hypotheses_hold and a_has_reported_inverse

    if confirmed:
        verdict = "CONFIRMED"
        notes = "Exact integer arithmetic confirms the witness: 1·2 is divisible by 2, both integers are nonzero, and 1·1 ≡ 1 (mod 2), so a=1 has inverse 1. The refuted statement is substantive: it requires b to be nonzero modulo m, not merely a nonzero integer."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The reported witness did not satisfy the claim's hypotheses and negation under exact integer arithmetic."

    result = {
        "record_id": "reddit_learnmath_5jdn3c",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
