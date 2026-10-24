r"""This vertex is adjacent to vertices in both $P_1 \cap P_1 \triangle P_2$ and $P_2 \cap P_1 \triangle P_2$."""

import json

RECORD_ID = "SE_math_3877823__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be named because the quote supplies no graph, "
    "distinguished vertex, adjacency relation, or definitions of P_1 and P_2."
)
REFUTATION_EXPLANATION = (
    "The finite sweep contains no admissible fully specified instances. The "
    "quoted assertion depends on missing contextual data, so neither the "
    "asserted adjacencies nor their failure can be checked without inventing "
    "data absent from the quote."
)
SEARCH_SPACE = (
    "Exactly the empty finite set of fully specified graph instances "
    "extractable from the supplied quote; all 0 such instances were swept in "
    "fixed tuple order."
)

fully_specified_instances = ()
for _instance in fully_specified_instances:
    raise AssertionError("The quote unexpectedly supplied an instance")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False))
