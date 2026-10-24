r"""At this point, $Y$ has a unique maximal clique (call it $H$) that contains $G \cap Y$.  Removing any element of $H$ from $Y$ will decrease $s(Y)$ by $1$."""

import json

RECORD_ID = "mse_297627__ans305070"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be specified from the supplied quote."
REFUTATION_EXPLANATION = (
    "The quote supplies no underlying graph, concrete sets G and Y, or definition "
    "of s, so neither the clique assertion nor the claimed change in s(Y) can be "
    "evaluated without inventing data."
)
SEARCH_SPACE = (
    "Exactly the empty set of fully specified candidate instances supplied by the "
    "quote (0 instances), iterated once in fixed order."
)


def main():
    candidates = ()
    for _candidate in candidates:
        raise AssertionError("The explicitly bounded candidate space must be empty")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
