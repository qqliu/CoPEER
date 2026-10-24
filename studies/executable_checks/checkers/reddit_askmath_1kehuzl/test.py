"""The map from the even natural numbers to all two-element sets of natural numbers, defined by n ↦ {n, n+1}, is a bijection."""

import json
from itertools import combinations

RECORD_ID = "reddit_askmath_1kehuzl"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "The two-element set {1, 2} is a concrete witness: it is a set of natural numbers but is not the image of any even natural number."
REFUTATION_EXPLANATION = "If {n, n+1} = {1, 2}, comparison of the smaller elements forces n = 1. Since 1 is not even, no even natural number maps to {1, 2}, so the map is not surjective and therefore not a bijection."
SEARCH_SPACE = "All 6 two-element subsets of {1, 2, 3, 4}, in lexicographic order, were checked against the even candidates n in {2, 4}. These are all possible positive even preimages for pairs in that bounded set, since equality with {n, n+1} forces n to be the pair's smaller element."

pairs = tuple(combinations(range(1, 5), 2))
even_candidates = tuple(n for n in range(1, 5) if n % 2 == 0)
missing = []

for pair in pairs:
    target = frozenset(pair)
    has_preimage = False
    for n in even_candidates:
        if frozenset((n, n + 1)) == target:
            has_preimage = True
    if not has_preimage:
        missing.append(pair)

assert len(pairs) == 6
assert even_candidates == (2, 4)
assert missing[0] == (1, 2)
assert all(n != 1 for n in even_candidates)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, sort_keys=False))
