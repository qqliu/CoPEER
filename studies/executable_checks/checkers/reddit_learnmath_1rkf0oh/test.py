"""The infimum alpha of the globally defined distance set S is positive, so alpha/2 is a valid positive radius for the proposed open ball."""

import itertools
import json
from fractions import Fraction

record_id = "reddit_learnmath_1rkf0oh"
grid = (Fraction(0, 1), Fraction(1, 2), Fraction(1, 1))
candidate_sets = []
zero_infimum_candidates = []

for size in range(1, len(grid) + 1):
    for candidate in itertools.combinations(grid, size):
        candidate_sets.append(candidate)
        if min(candidate) == Fraction(0, 1):
            zero_infimum_candidates.append(candidate)

assert len(candidate_sets) == 7
assert len(zero_infimum_candidates) == 4

result = {
    "record_id": record_id,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No certified witness: the quote does not define S or specify which x and y are admissible, so none of the enumerated candidate sets can be identified with the claimed distance set.",
    "refutation_explanation": "Being bounded below by 0 establishes existence of an infimum but does not establish that the infimum is positive. The supplied data omit the definition of S and all constraints needed to decide whether a zero-infimum candidate is admissible, so the claim is underdetermined.",
    "search_space": "Exhaustively swept all 7 nonempty subsets of the exact rational grid {0, 1/2, 1}. This is only an illustrative bounded candidate space, not an exhaustive space for the undefined set S."
}

print(json.dumps(result, separators=(",", ":")))
