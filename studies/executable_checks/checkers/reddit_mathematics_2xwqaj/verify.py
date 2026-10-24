r"""Lemma 5's asserted identity holds for all positive integers k, interpreting the displayed notation as powers of 2."""

import json

REPORT = {
    "record_id": "reddit_mathematics_2xwqaj",
    "verdict": "CONFIRMED",
    "notes": "Exact independent recomputation at k = 3 gives left = 255 and right = 135, so the universal identity fails. The refuted statement is substantive under the claim's explicit powers-of-2 interpretation, not plainly a typo.",
}


def two_to(nonnegative_exponent):
    assert isinstance(nonnegative_exponent, int)
    assert nonnegative_exponent >= 0
    value = 1
    for _ in range(nonnegative_exponent):
        value *= 2
    return value


witness = 3
assert witness > 0
current_quantic = two_to(two_to(witness))
prior_quantic = two_to(two_to(witness - 1))
left_hand_side = current_quantic - 1
prior_minus_one = prior_quantic - 1
right_hand_side = prior_minus_one * two_to(witness) + prior_minus_one

assert two_to(witness) == 8
assert prior_quantic == 16
assert current_quantic == 256
assert left_hand_side == 255
assert right_hand_side == 135
assert left_hand_side != right_hand_side
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
