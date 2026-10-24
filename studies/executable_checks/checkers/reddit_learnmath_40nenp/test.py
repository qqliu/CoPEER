"""A rational number a/b in [0,1] must satisfy digits(a) < digits(b)."""

import json


def decimal_digits(n):
    return len(str(n))


witnesses = []
checked = 0
for a in range(1, 10):
    for b in range(1, 10):
        if a < b:
            checked += 1
            if decimal_digits(a) >= decimal_digits(b):
                witnesses.append((a, b))

assert checked == 36
assert witnesses[0] == (1, 2)

result = {
    "record_id": "reddit_learnmath_40nenp",
    "outcome": "WITNESS_FOUND",
    "witness_description": "a = 1 and b = 2, so a/b = 1/2.",
    "refutation_explanation": "The fraction 1/2 lies in [0,1], but digits(1) = 1 and digits(2) = 1, so digits(a) < digits(b) is false.",
    "search_space": "All 36 ordered integer pairs (a,b) with 1 <= a < b <= 9, iterated lexicographically by a then b."
}
print(json.dumps(result, separators=(",", ":")))
