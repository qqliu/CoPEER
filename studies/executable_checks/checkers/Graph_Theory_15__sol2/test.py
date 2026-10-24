"""If a neighbor z in {x, y} is not u, then z must be some internal vertex vi of the path P (where 2 < i < n - 1)."""

import itertools
import json


REPORT = {
    "record_id": "Graph Theory_15__sol2",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete counterexample is reported: the quote does not specify the vertex of which z is a neighbor, any graph, the vertices of P, the value of n, or how x, y, and u relate to P.",
    "refutation_explanation": "The sweep finds the formal truth-table violation (A, B) = (True, False), but it also finds satisfying valuations. Because the missing graph/path data do not decide whether the violating valuation is realizable, that Boolean pair is not a mathematical witness and the claim cannot be refuted from the supplied quote alone.",
    "search_space": "Exactly the four Boolean pairs (A, B) produced by itertools.product((False, True), repeat=2), in that fixed order. A abbreviates \"z is a neighbor in {x, y} and z is not u\"; B abbreviates \"z is vi for some i with 2 < i < n - 1\". This exhausts only the conditional's truth table, not graph/path instances.",
}

truth_values = (False, True)
tested = []
first_formal_violation = None
saw_satisfying_valuation = False

for antecedent, consequent in itertools.product(truth_values, repeat=2):
    valuation = (antecedent, consequent)
    tested.append(valuation)
    if antecedent and not consequent:
        if first_formal_violation is None:
            first_formal_violation = valuation
    else:
        saw_satisfying_valuation = True

expected_domain = tuple(itertools.product(truth_values, repeat=2))
if tuple(tested) != expected_domain:
    raise AssertionError("The stated Boolean domain was not exhaustively swept")
if first_formal_violation != (True, False):
    raise AssertionError("Unexpected first formal truth-table violation")
if not saw_satisfying_valuation:
    raise AssertionError("The sweep should include satisfying valuations")

missing_semantic_data = (
    "vertex of which z is a neighbor",
    "graph",
    "vertices of P",
    "value of n",
    "relation of x, y, and u to P",
)
if first_formal_violation is not None and missing_semantic_data:
    computed_outcome = "NO_WITNESS_INCONCLUSIVE"
elif first_formal_violation is not None:
    computed_outcome = "WITNESS_FOUND"
else:
    computed_outcome = "NO_WITNESS_INCONCLUSIVE"

if computed_outcome != REPORT["outcome"]:
    raise AssertionError("The computed outcome and literal report disagree")
if tuple(REPORT) != (
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
):
    raise AssertionError("REPORT has unexpected keys")

print(json.dumps(REPORT, ensure_ascii=True, separators=(",", ":")))
