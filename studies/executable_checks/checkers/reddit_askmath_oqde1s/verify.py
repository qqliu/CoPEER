r"""From dem = a and den = b, de is a common multiple of a and b."""

import json

record_id = "reddit_askmath_oqde1s"
d, e, m, n = 1, 1, 1, 2
reported_a, reported_b, reported_de = 1, 2, 1

a = d * e * m
b = d * e * n
de = d * e
premises_verified = (a == reported_a and b == reported_b and de == reported_de)
is_common_multiple = (de % a == 0 and de % b == 0)

if premises_verified and not is_common_multiple:
    verdict = "CONFIRMED"
    notes = "Exact integer recomputation confirms the witness: dem=1=a and den=2=b, while de=1 is not divisible by b=2. The refuted statement is plainly a typo: the premises make de a common divisor of a and b, not a common multiple."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact integer recomputation does not validate the reported witness. The refuted statement appears to be plainly a typo confusing common divisor with common multiple."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}))
