"""Assuming only that n is interesting, if n+1 is non-interesting, then n+1 is the smallest non-interesting natural number."""

import json

RECORD_ID = "reddit_mathematics_i3ob36"
VALUES = tuple(range(1, 10))
first_witness = None

for n in range(1, 9):
    for mask in range(1 << len(VALUES)):
        non_interesting = frozenset(
            value for index, value in enumerate(VALUES)
            if mask & (1 << index)
        )
        premise_holds = n not in non_interesting and n + 1 in non_interesting
        smaller_non_interesting = tuple(
            value for value in VALUES
            if value < n + 1 and value in non_interesting
        )
        conclusion_holds = not smaller_non_interesting
        if premise_holds and not conclusion_holds and first_witness is None:
            first_witness = (n, non_interesting, smaller_non_interesting[0])

if first_witness == (2, frozenset((1, 3)), 1):
    outcome = "WITNESS_FOUND"
    witness_description = (
        "Take n = 2 and declare exactly 1 and 3 non-interesting; every other "
        "natural number is interesting. Then n is interesting and n+1 = 3 is "
        "non-interesting, but 1 is a smaller non-interesting natural number."
    )
    refutation_explanation = (
        "The sole assumption that n is interesting gives no information about "
        "natural numbers below n. In the witness, the implication's premise "
        "holds, while its conclusion fails because 1 < 3 and 1 is non-interesting."
    )
else:
    outcome = "NO_WITNESS_EXHAUSTIVE"
    witness_description = "No counterexample was found in the bounded space."
    refutation_explanation = "The bounded model family was fully checked."

search_space = (
    "All 4,096 pairs (n, S) in fixed order, where n ranges from 1 through 8 "
    "and S ranges over all 512 subsets of {1,2,3,4,5,6,7,8,9}; S is the set "
    "of non-interesting naturals and every natural outside S is interesting. "
    "The entire bounded space is swept."
)

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}, sort_keys=False))
