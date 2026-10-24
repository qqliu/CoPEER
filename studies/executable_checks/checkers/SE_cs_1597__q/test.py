'''That is, the optimal sum for a square array of size `n` can be determined by separately computing the optimal sum for each of the four sub-arrays of size `n-1`, and then maximising the sum of the sub-array and the element that was "left out".'''

import json

RECORD_ID = "SE_cs_1597__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be evaluated from the supplied quote alone."
REFUTATION_EXPLANATION = (
    "The quote does not define \"optimal sum\", the admissible array entries or "
    "selections, which four sub-arrays are intended, or how a single \"left out\" "
    "element is associated with an (n-1)-by-(n-1) sub-array. Supplying those "
    "definitions would invent data, so counterexample testing is inconclusive."
)
SEARCH_SPACE = (
    "The explicitly bounded candidate-instance space swept is the empty tuple (): "
    "exactly 0 arrays. No fully specified test instance can be formed from the "
    "supplied quote without inventing missing definitions or data."
)

candidate_instances = ()
checked = 0
for _instance in candidate_instances:
    checked += 1
assert checked == 0

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
