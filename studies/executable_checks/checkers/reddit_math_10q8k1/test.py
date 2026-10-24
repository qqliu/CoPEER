"""Any complex-valued function is constant."""

import json
from itertools import product


def main():
    domain = (0, 1)
    values = (0, 1)
    witness = None

    for outputs in product(values, repeat=len(domain)):
        if any(output != outputs[0] for output in outputs[1:]):
            witness = outputs
            break

    if witness != (0, 1):
        raise AssertionError("deterministic exhaustive search did not find the expected witness")

    result = {
        "record_id": "reddit_math_10q8k1",
        "outcome": "WITNESS_FOUND",
        "witness_description": "On the domain {0,1}, the function f defined by f(0)=0 and f(1)=1 is complex-valued (its integer values are also complex numbers) and is not constant.",
        "refutation_explanation": "The search finds f(0)=0 and f(1)=1. Since 0 != 1, this function takes two distinct values, contradicting the universal claim that every complex-valued function is constant.",
        "search_space": "All 4 functions from the ordered domain (0,1) to the ordered value set (0,1), enumerated by output tuples in lexicographic order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
