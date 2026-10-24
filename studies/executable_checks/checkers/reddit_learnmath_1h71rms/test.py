"""If a^2 is divisible by n, then a is divisible by n."""

import json

RECORD_ID = "reddit_learnmath_1h71rms"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "a = 2 and n = 4."
REFUTATION_EXPLANATION = "2^2 = 4 is divisible by 4, but 2 is not divisible by 4."
SEARCH_SPACE = (
    "All 272 ordered integer pairs (a, n) with 0 <= a <= 16 and "
    "1 <= n <= 16, iterated in increasing n and then increasing a; "
    "every pair was checked."
)

counterexamples = []
for n in range(1, 17):
    for a in range(17):
        if (a * a) % n == 0 and a % n != 0:
            counterexamples.append((a, n))

assert counterexamples
assert counterexamples[0] == (2, 4)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
