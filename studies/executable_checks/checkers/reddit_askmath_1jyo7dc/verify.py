r'''No fraction with denominator 500 can be equivalent to a fraction with denominator 9, 99, 999, and so on.'''

import json

left_denominator = 500
right_denominator = 0
for digit in (9,):
    right_denominator = right_denominator * 10 + digit

left_numerator = left_denominator
right_numerator = right_denominator

valid = (
    left_denominator == 500
    and right_denominator == 9
    and left_denominator != 0
    and right_denominator != 0
    and left_numerator == 500
    and right_numerator == 9
    and left_numerator * right_denominator
    == right_numerator * left_denominator
)

if valid:
    verdict = "CONFIRMED"
    notes = "Exact integer cross-multiplication verifies 500/500 = 9/9, so the literal universal statement is substantively false, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The reported witness does not satisfy the claim's denominator and exact-equivalence conditions; the statement is substantive, not plainly a typo."

result = {
    "record_id": "reddit_askmath_1jyo7dc",
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
