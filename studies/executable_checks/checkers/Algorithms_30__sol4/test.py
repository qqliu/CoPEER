"""those later sorts are *stable* and only reorder strings **within** the groups that share the same bit at position j"""

import json


def main():
    candidate_instances = ()
    for _instance in candidate_instances:
        raise AssertionError("The bounded candidate space is empty")

    result = {
        "record_id": "Algorithms_30__sol4",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be formed from the supplied quote alone.",
        "refutation_explanation": "The quote does not specify the strings, the bit position j, the sequence of later sorts, their keys, or their input and output states. Defining any of these would invent data absent from the quote, so the stability and within-group assertions cannot be evaluated.",
        "search_space": "Exactly the empty set of fully specified concrete sorting instances supplied by the quote (0 instances).",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
