"""If x<y and a<=b, then a*x<b*y always holds."""

import json

x = -2
y = -1
a = -2
b = -2

left_product = a * x
right_product = b * y
premises_hold = x < y and a <= b
conclusion_holds = left_product < right_product
witness_is_valid = premises_hold and not conclusion_holds

if witness_is_valid and left_product == 4 and right_product == 2:
    verdict = "CONFIRMED"
    notes = "Independent exact-integer recomputation verifies the premises and obtains a*x = 4 and b*y = 2, so 4 < 2 is false. The refuted statement is substantive, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Independent exact-integer recomputation does not validate the reported witness. The statement is substantive, not plainly a typo."

print(json.dumps({
    "record_id": "reddit_askmath_q8lalm",
    "verdict": verdict,
    "notes": notes
}, separators=(",", ":")))
