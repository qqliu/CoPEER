r"""For arbitrary real numbers x_1,…,x_n, if their sum is n, then their product is at most 1."""

import json

record_id = "reddit_learnmath_9m5f5w"
n = 3
witness = (-1, -1, 5)

total = 0
product = 1
all_integers = True
for value in witness:
    if not isinstance(value, int):
        all_integers = False
    total += value
    product *= value

valid = (
    isinstance(n, int)
    and n > 0
    and len(witness) == n
    and all_integers
    and total == n
    and product > 1
)

if valid:
    verdict = "CONFIRMED"
    notes = "Exact integer arithmetic verifies that (-1)+(-1)+5=3 and (-1)(-1)(5)=5>1. Since integers are real numbers, this is a valid counterexample. The refuted statement is substantive, not plainly a typo; it needs an additional restriction such as nonnegative inputs."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact recomputation did not validate the proposed witness; the refuted statement would therefore not be established. The issue would be substantive, not plainly a typo."

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
