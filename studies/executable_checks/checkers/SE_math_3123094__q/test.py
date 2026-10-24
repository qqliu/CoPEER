"""A clique with 6 vertex is a counterexample. Since there is a circle for each vertex pair that contains these vertex, but the graph is not 2-vertex-connected or ?"""

import json

RECORD_ID = "SE_math_3123094__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No counterexample can be certified from the supplied text."
REFUTATION_EXPLANATION = (
    "The text names a six-vertex clique but does not state the proposition to "
    "which it is allegedly a counterexample, define \"circle,\" or complete the "
    "dangling alternative after \"or ?\". Therefore the required violation "
    "predicate is not determined by the permitted data."
)
SEARCH_SPACE = (
    "Exactly one supplied candidate description was swept: the six-vertex "
    "clique. It was checked only for whether the supplied quote specifies a "
    "complete claim and a decidable violation predicate; it does not."
)


def main():
    candidates = (("clique", 6),)
    decisive_candidates = []
    for graph_kind, vertex_count in candidates:
        claim_to_refute_is_specified = False
        circle_is_defined = False
        alternative_is_complete = False
        if (
            graph_kind == "clique"
            and vertex_count == 6
            and claim_to_refute_is_specified
            and circle_is_defined
            and alternative_is_complete
        ):
            decisive_candidates.append((graph_kind, vertex_count))

    assert not decisive_candidates
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
