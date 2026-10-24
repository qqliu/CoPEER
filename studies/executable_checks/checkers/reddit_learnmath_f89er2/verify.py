r"""For all integers p and n, if p divides n^2 then p divides n."""

import json

record_id = "reddit_learnmath_f89er2"
p = 4
n = 2
square = n * n
premise = divmod(square, p)[1] == 0
conclusion = divmod(n, p)[1] == 0

if premise and not conclusion:
    verdict = "CONFIRMED"
    notes = "Exact recomputation confirms the witness: with p = 4 and n = 2, n squared is 4, so 4 divides n squared, while 4 does not divide 2. The refuted statement is substantive as written, not plainly a typo; it would require an additional hypothesis such as p being prime."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact recomputation does not validate the proposed witness. The statement under review is substantive as written, not plainly a typo."

result = {"record_id": record_id, "verdict": verdict, "notes": notes}
print(json.dumps(result, separators=(",", ":")))
