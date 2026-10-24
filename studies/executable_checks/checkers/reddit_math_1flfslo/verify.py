"""For all real a,b and all z>0, if a<=b+z, then a<=b."""

import json

REPORT = {
    "record_id": "reddit_math_1flfslo",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: exact integer arithmetic gives z=1>0 and a=0<=b+z=0, while a<=b is false. The refuted statement is substantively false, not plainly a typo."
}

a = 7 - 7
b = 3 - 4
z = 5 - 4

assert (a, b, z) == (0, -1, 1)
assert z > 0
assert a <= b + z
assert not (a <= b)

print(json.dumps(REPORT, separators=(",", ":")))
