"""We can assume $v_1$ will be adjacent to all $v_i(i=k+1,...,n-2).$"""

import json

RECORD_ID = "SE_math_3412684__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness can be specified because the supplied quote contains no concrete "
    "graph instance, values of k and n, or adjacency relation."
)
REFUTATION_EXPLANATION = (
    "The phrase \"We can assume\" is context-dependent, and the quote supplies "
    "neither hypotheses nor definitions that would make the asserted adjacency "
    "finitely testable. The empty set of supplied graph instances was swept, so "
    "this does not establish or refute the claim."
)
SEARCH_SPACE = (
    "Exactly the 0 graph instances explicitly supplied by the source quote, "
    "represented by the empty tuple; all 0 were examined in fixed tuple order."
)


def main():
    supplied_graph_instances = ()
    examined = 0
    for _instance in supplied_graph_instances:
        examined += 1
    assert examined == 0

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
