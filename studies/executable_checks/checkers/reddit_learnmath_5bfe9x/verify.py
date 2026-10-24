r"""From nq^2 = p^2, it follows that n divides p."""

import json

record_id = "reddit_learnmath_5bfe9x"
n = 4
p = 2
q = 1

left_side = n * q * q
right_side = p * p
quotient, remainder = divmod(p, n)

assert left_side == right_side
assert remainder != 0
assert p != n * quotient

verdict = "CONFIRMED"
notes = "Exact integer recomputation confirms the witness: 4·1·1 = 2·2 = 4, while divmod(2, 4) has nonzero remainder 2, so 4 does not divide 2. The refuted statement is substantive, not plainly a typo; it requires an additional hypothesis such as n being squarefree."
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
