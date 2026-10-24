"""Now, during a correctness proof we would show that `foo` is executed exactly once per node; that is, $B = n$."""

import json


def main():
    supplied_instances = ()
    for _instance in supplied_instances:
        raise AssertionError("The source quote supplies no concrete instances")

    result = {
        "record_id": "SE_cs_23593__a23595",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness: the quote supplies no concrete algorithm, input, node set, execution trace, or definitions of B and n.",
        "refutation_explanation": "The claim cannot be tested from the supplied source alone. Arbitrarily assigning unequal integers to B and n would invent an instance rather than produce a valid counterexample.",
        "search_space": "All concrete algorithm/input instances supplied by source_quote: the empty set (0 instances), exhaustively enumerated in fixed tuple order.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
