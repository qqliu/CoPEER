"""For odd n with floor(n/2) even, (floor(n/2)+1)*2 equals n+2."""

import json

record_id = "reddit_learnmath_8yjpp7"
n = 1
half = n // 2
hypotheses_hold = (n % 2 == 1) and (half % 2 == 0)
left_side = (half + 1) * 2
right_side = n + 2
witness_refutes = hypotheses_hold and (left_side != right_side)

if witness_refutes:
    verdict = "CONFIRMED"
    notes = "Exact integer recomputation at n = 1 gives floor(n/2) = 0; n is odd and 0 is even, while the two sides are 2 and 3. Thus the witness genuinely refutes the universal claim. The refuted statement is plainly an off-by-one typo, not a substantive mathematical assertion."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact integer recomputation does not validate the proposed witness. The statement appears to be an off-by-one typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
