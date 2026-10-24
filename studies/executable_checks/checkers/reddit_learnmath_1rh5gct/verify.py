r"""For every positive integer n, 1^2 + 2^2 + … + n^2 = n(n + 1)(2n + 1)."""

import json

record_id = "reddit_learnmath_1rh5gct"
candidate = 1
left_hand_side = 0
current = 1
while current <= candidate:
    left_hand_side += current * current
    current += 1
right_hand_side = candidate * (candidate + 1) * (2 * candidate + 1)

valid_witness = (
    isinstance(candidate, int)
    and candidate > 0
    and left_hand_side == 1
    and right_hand_side == 6
    and left_hand_side != right_hand_side
)

if valid_witness:
    verdict = "CONFIRMED"
    notes = "Exact integer recomputation at the positive-integer witness n = 1 gives left-hand side 1 and right-hand side 6, so the universal claim fails. The refuted statement is plainly a typo: it omits the usual factor of 1/6."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The reported witness did not survive exact integer recomputation; the statement appears to be a typo rather than a substantive claim."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
