"""Blind bounded counterexample search.

Target claim (verbatim):
we have |δ(Vi)| ≥2k for every i = 1, 2, . . . , m.
"""

import json


RECORD_ID = "Algorithms_38__sol4"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness can be evaluated: the quote supplies no values or definitions "
    "for δ, Vi, k, or m."
)
REFUTATION_EXPLANATION = (
    "The inequality cannot be checked from the permitted data because neither "
    "δ(Vi) nor its cardinality, the indexed sets Vi, nor the integer parameters "
    "k and m are defined. The exhaustive sweep therefore contains zero fully "
    "specified instances and cannot support or refute the claim."
)
SEARCH_SPACE = (
    "Exactly the empty tuple of fully specified mathematical instances supplied "
    "by the quote (0 instances)."
)


def main():
    supplied_instances = ()
    witness = None

    for instance in supplied_instances:
        raise AssertionError("The declared search space must be empty")

    if witness is not None:
        raise AssertionError("No witness can arise from an empty search space")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
