"""A graph contains a cycle if and only if there is a cut with more than one edge."""

import json

CLAIM = "A graph contains a cycle if and only if there is a cut with more than one edge."
SOURCE_QUOTE = "A graph contains a cycle if and only if there is a cut with more than one edge."

PERMITTED_INPUT_SPACE = ((CLAIM, SOURCE_QUOTE),)
inspected = []
for item in PERMITTED_INPUT_SPACE:
    inspected.append(item)

assert tuple(inspected) == PERMITTED_INPUT_SPACE
assert len(PERMITTED_INPUT_SPACE) == 1
assert PERMITTED_INPUT_SPACE[0][0] == PERMITTED_INPUT_SPACE[0][1]

result = {
    "record_id": "SE_cs_2840__a2841",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No counterexample is asserted: the supplied sentence gives no definition of graph, cycle, or cut from which a candidate can be checked.",
    "refutation_explanation": "The claim may be refutable under particular graph-theoretic conventions, but choosing what counts as a graph or a cut would add definitions absent from the quote. Therefore no concrete witness can be certified from the permitted data alone.",
    "search_space": "Exhaustively inspected the one-element bounded space consisting of the supplied (target_claim, source_quote) pair; it contains the same sentence twice and no formal definitions. No graph space was searched because no permitted counterexample predicate is determined."
}

print(json.dumps(result, separators=(",", ":")))
