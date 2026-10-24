r"""We will show that for any graph G and any integer K >=1, the following equivalence holds: G has a vertex cover of size <=K => the river crossing instance (G, k) with k := K + 1 is feasible."""

import json
from itertools import product

REPORT = {
    "record_id": "Algorithms_11__sol1",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be evaluated because the supplied quote does not define when the river crossing instance (G, k) is feasible.",
    "refutation_explanation": "The bounded sweep finds both a truth assignment that violates the displayed implication and one that satisfies it when feasibility is treated as an opaque Boolean atom. Thus the implication is not determined by the quote alone; neither assignment supplies a mathematical graph counterexample without the missing feasibility definition.",
    "search_space": "All 4 Boolean assignments (antecedent, consequent), in fixed False-before-True product order. This exhaustively checks propositional underdetermination only, not any space of graph instances.",
}

first_violating_completion = None
first_satisfying_completion_with_true_antecedent = None
swept = []

for antecedent, consequent in product((False, True), repeat=2):
    swept.append((antecedent, consequent))
    implication_holds = (not antecedent) or consequent
    if not implication_holds and first_violating_completion is None:
        first_violating_completion = (antecedent, consequent)
    if antecedent and implication_holds and first_satisfying_completion_with_true_antecedent is None:
        first_satisfying_completion_with_true_antecedent = (antecedent, consequent)

if first_violating_completion is not None and first_satisfying_completion_with_true_antecedent is not None:
    derived_outcome = "NO_WITNESS_INCONCLUSIVE"
else:
    derived_outcome = "CLAIM_NOT_FINITELY_REFUTABLE"

assert swept == [
    (False, False),
    (False, True),
    (True, False),
    (True, True),
]
assert first_violating_completion == (True, False)
assert first_satisfying_completion_with_true_antecedent == (True, True)
assert derived_outcome == REPORT["outcome"]

print(json.dumps(REPORT, separators=(",", ":")))
