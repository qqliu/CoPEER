r"""u ->v does *not* lie in E1 intersect E2, and hence appears in exactly one of bE or E. In other words, **edge u ->v crosses exactly one of the new cuts**."""

import json
from itertools import product

REPORT = {
    "record_id": "Algorithms_24__sol4",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No claim-level witness is identifiable. The first abstract completion with the stated non-intersection but not exactly-one membership is E1=False, E2=False, bE=False, E=False; however, the quote does not establish that this completion is admissible for edge u ->v.",
    "refutation_explanation": "The quote supplies no definitions of E1, E2, bE, E, the new cuts, or constraints connecting their memberships. Standard Boolean semantics for intersection and exactly-one membership admit both supporting and violating completions, so the bounded sweep demonstrates underdetermination rather than a counterexample to the contextual claim.",
    "search_space": "All 16 fixed-order Boolean assignments to membership of edge u ->v in (E1, E2, bE, E), with False preceding True; assignments were classified when not (E1 and E2) holds."
}

violating_completions = []
supporting_completions = []
assignments_examined = 0
for in_e1, in_e2, in_be, in_e in product((False, True), repeat=4):
    assignments_examined += 1
    stated_nonintersection = not (in_e1 and in_e2)
    exactly_one = in_be != in_e
    if stated_nonintersection:
        completion = (in_e1, in_e2, in_be, in_e)
        if exactly_one:
            supporting_completions.append(completion)
        else:
            violating_completions.append(completion)

if assignments_examined != 16:
    raise AssertionError("the declared finite truth-assignment space was not swept")
if not violating_completions or not supporting_completions:
    raise AssertionError("the sweep did not demonstrate underdetermination")
if violating_completions[0] != (False, False, False, False):
    raise AssertionError("the reported first abstract completion drifted")

print(json.dumps(REPORT, separators=(",", ":")))
