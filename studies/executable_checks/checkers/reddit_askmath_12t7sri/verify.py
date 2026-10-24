r'''The displayed formula for the remainder r(x) makes the asserted equality f(x)=(a_n/b_n)g(x)+r(x) hold when deg(f)=deg(g).'''

import json

record_id = "reddit_askmath_12t7sri"
a = (-1, -1, -1)
b = (0, -1, -1)

same_positive_degree = len(a) == len(b) and len(a) > 1
degree_conditions = same_positive_degree and a[-1] != 0 and b[-1] != 0

# Represent every coefficient over the common denominator b_n.
a_n = a[-1]
b_n = b[-1]
scaled_remainder = (
    a[0] * b_n - a_n * a[0],
    a[1] * b_n - a_n * b[1],
    0,
)
scaled_left = tuple(coefficient * b_n for coefficient in a)
scaled_right = tuple(
    a_n * b[index] + scaled_remainder[index]
    for index in range(len(a))
)

witness_valid = (
    degree_conditions
    and scaled_left == (1, 1, 1)
    and scaled_right == (0, 1, 1)
    and scaled_left != scaled_right
)

if witness_valid:
    verdict = "CONFIRMED"
    notes = "The witness is valid. Exact integer cross-multiplication gives RHS constant coefficient 0 while f has constant coefficient -1. The refuted statement is plainly a typo rather than a substantive mathematical error: the displayed constant term uses a_0 where b_0 is required."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The reported witness did not independently reproduce; the alleged issue appears to concern a plain typo rather than a substantive mathematical statement."

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
