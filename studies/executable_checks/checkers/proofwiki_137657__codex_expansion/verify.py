r"""If B is known to have occurred, the conditional probability of A given B equals Pr(A ∩ B)."""

import json
from math import gcd

RECORD_ID = "proofwiki_137657__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = "Exact recomputation on the reported uniform two-outcome space gives Pr(A | B)=1/1 and Pr(A ∩ B)=1/2, so the witness genuinely refutes the claim. The refuted statement is a substantive false probability identity, not plainly a typo."


def reduced_ratio(numerator, denominator):
    if denominator <= 0:
        raise ValueError("probability denominator must be positive")
    common = gcd(numerator, denominator)
    return numerator // common, denominator // common


def main():
    outcomes = frozenset((0, 1))
    event_a = frozenset((0,))
    event_b = frozenset((0,))
    observed = 0

    if observed not in event_b or not event_b.issubset(outcomes):
        raise AssertionError("the reported observation does not establish B")
    if not event_a.issubset(outcomes):
        raise AssertionError("A is not an event in the reported space")

    overlap_count = len(event_a.intersection(event_b))
    conditional = reduced_ratio(overlap_count, len(event_b))
    joint = reduced_ratio(overlap_count, len(outcomes))

    if conditional != (1, 1) or joint != (1, 2):
        raise AssertionError("reported exact probabilities were not reproduced")
    if conditional[0] * joint[1] == joint[0] * conditional[1]:
        raise AssertionError("the two exact probabilities are equal")

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
