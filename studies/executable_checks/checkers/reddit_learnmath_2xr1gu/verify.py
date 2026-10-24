"""The inductive transition for the sum of squares obtains P(n+1) from P(n) by adding (n+1)."""

import json


def squares_through(limit):
    total = 0
    term = 1
    while term <= limit:
        total += term * term
        term += 1
    return total


record_id = "reddit_learnmath_2xr1gu"
notes = (
    "Exact recomputation at n=1 gives S(1)+(1+1)=1+2=3, while "
    "S(2)=1·1+2·2=5. Thus the stated transition is false on the reported "
    "witness; the required increment is (n+1) squared. This is a substantive "
    "mathematical error, not plainly a typo."
)
n = 1
sum_at_n = squares_through(n)
claimed_sum_at_next = sum_at_n + n + 1
actual_sum_at_next = squares_through(n + 1)
if (sum_at_n, claimed_sum_at_next, actual_sum_at_next) == (1, 3, 5):
    verdict = "CONFIRMED"
else:
    verdict = "CANNOT_REPRODUCE"
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
