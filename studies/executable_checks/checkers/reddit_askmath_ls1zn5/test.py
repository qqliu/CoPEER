"""Adding the removed edges back leaves all pairwise distances in G' and G equal."""

import json


def main():
    supplied_graph_instances = ()
    for _instance in supplied_graph_instances:
        raise AssertionError("The explicitly supplied instance space is empty")

    result = {
        "record_id": "reddit_askmath_ls1zn5",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be formed from the supplied data because no vertices, edges, removed-edge set, or distance convention is specified.",
        "refutation_explanation": "The supplied claim and quote assert equality of distances but provide no concrete graphs or conditions defining G and G'. Inventing a graph model or missing hypotheses would violate the blind-data restriction, so the empty set of supplied graph instances yields no witness and the result is inconclusive.",
        "search_space": "Exactly the empty finite set of concrete graph instances explicitly specified by the target claim and source quote (0 instances).",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
