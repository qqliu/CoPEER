"""The only positive integer that can divide both an odd number and an even number is 1."""

import json

RECORD_ID = "reddit_learnmath_1b5n8w6"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The positive integer 3 divides the odd number 3 and the even number 6."
)
REFUTATION_EXPLANATION = (
    "Since 3 is a positive integer greater than 1, and 3 % 3 == 0 and "
    "6 % 3 == 0, this is a counterexample to the claim that only 1 can "
    "divide both an odd number and an even number."
)
SEARCH_SPACE = (
    "All 432 ordered triples (d, o, e) with 1 <= d, o, e <= 12, o odd, "
    "and e even, checked in increasing lexicographic loop order; every "
    "triple was tested for d != 1, o % d == 0, and e % d == 0."
)

witnesses = []
tested = 0
for d in range(1, 13):
    for o in range(1, 13):
        if o % 2 != 1:
            continue
        for e in range(1, 13):
            if e % 2 != 0:
                continue
            tested += 1
            if d != 1 and o % d == 0 and e % d == 0:
                witnesses.append((d, o, e))

assert tested == 432
assert witnesses
assert witnesses[0] == (3, 3, 6)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":"), sort_keys=True))
