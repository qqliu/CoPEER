"""The Euler characteristic is only defined for a 2-dimensional manifold."""

import json


def main():
    explicit_mentions = (("2 dimensional manifold", 2),)
    non_two_dimensional = tuple(
        name for name, dimension in explicit_mentions if dimension != 2
    )
    assert non_two_dimensional == ()

    result = {
        "record_id": "reddit_math_1crm7dl",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete counterexample is supplied: the only object class explicitly named is a 2-dimensional manifold.",
        "refutation_explanation": "The source quote merely repeats the claim and provides neither a definition of Euler characteristic nor any non-2-dimensional object on which it is defined, so the bounded textual sweep cannot decide or refute the claim.",
        "search_space": "Exactly one explicit object-class mention was swept: ('2 dimensional manifold', 2). No non-2-dimensional candidate occurs in the supplied source data.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
