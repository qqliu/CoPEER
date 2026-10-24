r"""Claim 1. G is r-connected (remains connected after removing any r - 1 vertices)."""

import json

CLAIM = "Claim 1. G is r-connected (remains connected after removing any r - 1 vertices)."
SOURCE_QUOTE = "Claim 1. G is r-connected (remains connected after removing any r - 1 vertices)."
SUPPLIED_GRAPH_R_INSTANCES = ()

REPORT = {
    "record_id": "Graph Theory_1__Graph Theory_1_3_old",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness is determined because the quote specifies neither the graph G nor the integer r.",
    "refutation_explanation": "The property can be checked only after G and r are supplied. The quote gives no vertex set, edge set, or value of r, so a bounded search over unrelated graphs would not refute the stated claim about G.",
    "search_space": "Exhaustive sweep of the explicitly supplied graph/r-instance tuple (), containing exactly 0 instances.",
}

examined = 0
first_counterexample = None
for graph_r_instance in SUPPLIED_GRAPH_R_INSTANCES:
    examined += 1
    raise AssertionError("A graph/r instance was encountered without a supplied representation.")

search_complete = examined == len(SUPPLIED_GRAPH_R_INSTANCES)
if first_counterexample is not None:
    computed_outcome = "WITNESS_FOUND"
elif search_complete and examined == 0:
    computed_outcome = "NO_WITNESS_INCONCLUSIVE"
else:
    computed_outcome = "NO_WITNESS_EXHAUSTIVE"

computed_search_space = (
    "Exhaustive sweep of the explicitly supplied graph/r-instance tuple (), "
    "containing exactly " + str(examined) + " instances."
)

assert CLAIM == SOURCE_QUOTE
assert search_complete
assert computed_outcome == REPORT["outcome"]
assert computed_search_space == REPORT["search_space"]
assert first_counterexample is None
assert tuple(REPORT) == (
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
)

print(json.dumps(REPORT, separators=(",", ":")))
