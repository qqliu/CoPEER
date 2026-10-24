"""From P = 2(L + W), the submitted Method 2 rearrangement yields L = W - (P/2)."""

import json
from fractions import Fraction

record_id = "reddit_learnmath_17yc2bm"
length = 1
width = 1
perimeter = 4

premise_holds = perimeter == 2 * (length + width)
claimed_right_side = Fraction(2 * width - perimeter, 2)
witness_refutes_claim = premise_holds and claimed_right_side != Fraction(length, 1)

if witness_refutes_claim:
    verdict = "CONFIRMED"
    notes = "Exact integer recomputation at L=1, W=1, P=4 verifies the premise, while W-(P/2)=-1, not 1. The refuted statement is plainly a sign/order typo; the correct rearrangement is L=P/2-W."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The reported witness does not exactly refute the claim. The statement appears intended as an algebraic rearrangement, not a substantive theorem."

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
