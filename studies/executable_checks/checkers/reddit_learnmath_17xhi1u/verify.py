r"""The stated assumptions imply x_n < 4 for every natural n."""

import json

RECORD_ID = "reddit_learnmath_17xhi1u"
VERDICT = "CONFIRMED"
NOTES = "Exact recomputation confirms the witness: x_1=1, x_2=4, and the recurrence applies only from n=3 onward. A real nonnegative continuation exists recursively because each radicand 3x_{n-1}+1 is positive. Thus the strict bound already fails at natural index 2. This is mathematically valid but plainly an indexing typo rather than a substantive counterexample to the likely intended recurrence starting at n=2."

x_1 = 1
x_2 = 4
witness_index = 2
first_recurrence_index = 3

assert x_1 == 1
assert witness_index >= 1
assert witness_index < first_recurrence_index
assert not x_2 < 4

# Starting with x_2 >= 0, recursive continuation is valid over the reals:
# if a preceding term is nonnegative, then 3 times it plus 1 is positive,
# so its unique nonnegative square root exists and is again nonnegative.
assert x_2 >= 0
assert 3 > 0
assert 1 > 0
first_radicand = 3 * x_2 + 1
assert first_radicand == 13
assert first_radicand > 0

result = {
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}
print(json.dumps(result, separators=(",", ":")))
