"""The displayed Broder Chain defines a valid transition from every near-perfect matching when the selected edge satisfies x=a_{M_{t-1}} and y≠b_{M_{t-1}}."""

import json

RECORD_ID = "arxiv_2505.21645v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be named from the supplied data because it contains "
    "no fully specified graph, matching, edge, or interpretation of the indexed symbols."
)
REFUTATION_EXPLANATION = (
    "The quote gives only an update expression. It does not define near-perfect "
    "matching, valid transition, a_M, b_M, f_M, the admissible selected edges, or "
    "whether f_M(x) is defined under the stated condition. Consequently the expression "
    "cannot be evaluated or checked for validity without inventing definitions."
)
SEARCH_SPACE = (
    "The exact finite space swept is the empty tuple of fully specified transition "
    "instances supplied by the quote (cardinality 0), visited in tuple order; this "
    "empty sweep is not evidence that the universal claim is true."
)


def search_source_supplied_instances():
    instances = ()
    witness = None
    for instance in instances:
        witness = instance
        break
    assert witness is None
    assert len(instances) == 0
    return {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }


if __name__ == "__main__":
    result = search_source_supplied_instances()
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
