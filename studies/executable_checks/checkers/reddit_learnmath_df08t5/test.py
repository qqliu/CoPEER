"""There exists a positive integer n such that (1+1/n)^n is an upper bound for all real numbers."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_df08t5"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = "No single concrete pair (n, x) refutes the existential claim: it only shows that the selected n fails. For every tested n from 1 through 1000, the exact real number x = ((n+1)/n)^n + 1 exceeds the proposed bound for that n."
REFUTATION_EXPLANATION = "Negating the claim requires showing that every positive integer n fails, an infinite requirement that cannot be established by an exhaustive bounded search. The finite sweep verifies a uniform-looking construction on its stated range but is not a finite counterexample to the existential claim."
SEARCH_SPACE = "Exactly the 1000 generated pairs (n, x) with n in {1, 2, ..., 1000} and x = Fraction(n+1, n)^n + 1, checked in increasing order of n using exact rational arithmetic."

for n in range(1, 1001):
    proposed_bound = Fraction(n + 1, n) ** n
    candidate_real = proposed_bound + 1
    if not candidate_real > proposed_bound:
        raise AssertionError("exact comparison failed")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
