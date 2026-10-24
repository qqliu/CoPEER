"""1 is the largest natural number."""

import json

REPORT = {
    "record_id": "reddit_learnmath_ya047e",
    "verdict": "CONFIRMED",
    "notes": "The statement is substantive, not plainly a typo: exact integer arithmetic confirms that 2 is a natural number and 2 > 1.",
}

one = 1
witness = one + one
assert type(witness) is int
assert witness >= 0
assert witness == 2
assert witness > one

print(json.dumps(REPORT, separators=(",", ":")))
