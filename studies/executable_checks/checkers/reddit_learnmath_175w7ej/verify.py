r"""From (a - b)^2 = (b - a)^2, taking square roots implies a - b = b - a."""

import json


def main():
    a = -2
    b = -1
    forward = a - b
    reverse = b - a
    premise_holds = forward * forward == reverse * reverse
    conclusion_fails = forward != reverse
    established = premise_holds and conclusion_fails

    if established:
        verdict = "CONFIRMED"
        notes = "The refuted statement is substantive, not plainly a typo: equal squares imply equality only up to sign, since taking the principal square root gives an absolute value."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The reported witness does not refute the claim."

    print(json.dumps({
        "record_id": "reddit_learnmath_175w7ej",
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
