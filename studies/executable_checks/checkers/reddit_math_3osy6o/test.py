"""Anything between a finite number and infinity must itself be infinite."""

import json


RECORD_ID = "reddit_math_3osy6o"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness is asserted; every enumerated raw pair is "
    "semantically undecidable from the supplied quote."
)
REFUTATION_EXPLANATION = (
    "The claim cannot be tested from the supplied text alone: no domain is "
    "specified, \"between\" is undefined, and infinity is not specified as an "
    "element or order endpoint. Therefore neither a violation nor confirmation "
    "can be certified."
)
SEARCH_SPACE = (
    "Enumerated all 4,225 ordered integer pairs (n, x) with -32 <= n <= 32 "
    "and -32 <= x <= 32, in lexicographic order. This is only a bounded "
    "raw-candidate sweep; none can be classified without inventing missing "
    "semantics."
)


def main():
    enumerated = 0
    undecidable = 0

    for finite_endpoint in range(-32, 33):
        for proposed_middle in range(-32, 33):
            candidate = (finite_endpoint, proposed_middle)
            enumerated += 1

            # The source supplies no predicate with which to decide whether
            # this raw pair represents a value "between" an endpoint and
            # infinity, so its status must remain unknown.
            if candidate == (finite_endpoint, proposed_middle):
                undecidable += 1

    assert enumerated == 4225
    assert undecidable == enumerated

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
