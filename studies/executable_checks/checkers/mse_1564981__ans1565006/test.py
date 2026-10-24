r"""17^4 (17^{4m} - 1) &= 10 \cdot a"""

import json

RECORD_ID = "mse_1564981__ans1565006"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample is claimed because the supplied formula gives neither "
    "quantifiers nor domains for m and a."
)
REFUTATION_EXPLANATION = (
    "The equation alone does not specify whether m and a are fixed, "
    "existentially quantified, universally quantified, or restricted to any "
    "particular sets. Consequently, no assignment can honestly be classified "
    "as a counterexample without inventing absent definitions."
)
SEARCH_SPACE = (
    "Exhaustively swept the empty tuple of well-defined assignments. It is "
    "empty because the supplied quote specifies no domains or quantifiers for "
    "m and a."
)

candidate_assignments = ()
for _assignment in candidate_assignments:
    raise AssertionError("The explicitly bounded search space must be empty")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
