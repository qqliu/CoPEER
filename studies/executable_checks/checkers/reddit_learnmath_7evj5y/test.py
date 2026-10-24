"""The displayed case definition gives a function g on all of (0,2)∪{4}."""

import json


def in_declared_domain(x):
    return (0 < x < 2) or x == 4


def displayed_definition_applies(x):
    # Both displayed cases are introduced only "for x in (0,2)".
    return 0 < x < 2


candidate_points = (4,)
witnesses = []
for x in candidate_points:
    if in_declared_domain(x) and not displayed_definition_applies(x):
        witnesses.append(x)

assert witnesses == [4]

result = {
    "record_id": "reddit_learnmath_7evj5y",
    "outcome": "WITNESS_FOUND",
    "witness_description": "x=4 is a declared domain element, but neither displayed case assigns g(4).",
    "refutation_explanation": "The words \"for x in (0,2)\" restrict the displayed cases to inputs in (0,2). Although one inner condition tests x=4, that condition cannot apply outside the stated outer interval. Thus g is undefined at the declared domain point 4, contradicting the claim that the definition gives a function on all of (0,2)∪{4}.",
    "search_space": "Exhaustively checked the explicitly bounded singleton candidate space {4}, the only separately listed domain point outside (0,2).",
}
print(json.dumps(result, separators=(",", ":")))
