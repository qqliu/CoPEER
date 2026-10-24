r"""For an arbitrary fixed natural number k, P(1) and P(k) suffice to imply P(k+1)."""

import json


def predicate(n):
    return n == 1 or n == 2


def main():
    k = 2
    is_natural = isinstance(k, int) and not isinstance(k, bool) and k >= 0
    hypotheses_hold = predicate(1) and predicate(k)
    conclusion_holds = predicate(k + 1)
    witness_refutes_claim = is_natural and hypotheses_hold and not conclusion_holds

    if witness_refutes_claim:
        verdict = "CONFIRMED"
        notes = "The witness is valid: with k = 2 and P(n) defined by n in {1, 2}, P(1) and P(k) are true but P(k+1) is false. The refuted statement is substantive, not plainly a typo; it lacks any condition connecting P(k) to P(k+1)."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The reported witness does not refute the claim."

    result = {
        "record_id": "reddit_math_5wlvhh",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
