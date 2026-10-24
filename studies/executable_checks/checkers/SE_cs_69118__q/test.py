"""- recursivly call the algorithm for n-1
        - take the lower cost edge between v0-->vn and v(n-1)-->vn"""

import json

RECORD_ID = "SE_cs_69118__q"
TARGET_CLAIM = "- recursivly call the algorithm for n-1\n        - take the lower cost edge between v0-->vn and v(n-1)-->vn"
SOURCE_QUOTE = "- recursivly call the algorithm for n-1\n        - take the lower cost edge between v0-->vn and v(n-1)-->vn"
WITNESS_DESCRIPTION = "No concrete witness can be defined from the supplied text alone."
REFUTATION_EXPLANATION = "The supplied text is an algorithm fragment, not a truth-valued correctness claim. It specifies neither the input objects and edge-cost domain nor the algorithm's required output or correctness predicate, so no candidate can be classified as a counterexample without inventing definitions."
SEARCH_SPACE = "Exactly the singleton space containing the one supplied (target_claim, source_quote) pair; that pair is inspected once in fixed order."


def main():
    bounded_space = ((TARGET_CLAIM, SOURCE_QUOTE),)
    inspected = 0
    for target_claim, source_quote in bounded_space:
        inspected += 1
        if target_claim != TARGET_CLAIM or source_quote != SOURCE_QUOTE:
            raise AssertionError("bounded-space entry changed")
    if inspected != 1:
        raise AssertionError("singleton space was not exhaustively inspected")

    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
