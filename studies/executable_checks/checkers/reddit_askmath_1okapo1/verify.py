r'''Dividing both sides by x is valid without imposing the precondition x ≠ 0.'''

import json
from fractions import Fraction

record_id = "reddit_askmath_1okapo1"
candidate = 0
left = (candidate + 1) * (candidate + 1)
right = 1

undefined_count = 0
for numerator in (left, right):
    try:
        Fraction(numerator, candidate)
    except ZeroDivisionError:
        undefined_count += 1

if left == right and undefined_count == 2:
    verdict = "CONFIRMED"
    notes = "Exact recomputation confirms the witness x = 0: (x + 1)(x + 1) = 1, but exact rational division by x raises ZeroDivisionError on both sides. The refuted statement is a substantive mathematical error, not a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Independent exact recomputation did not validate the proposed witness. The statement would be substantive rather than a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
