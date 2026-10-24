"""The finite index set in Case 2 has a maximum that can be used as N."""

import itertools
import json


def main():
    witness_description = (
        "No concrete witness can be identified. The empty membership pattern is an "
        "abstract obstruction to taking a maximum, but the quote does not determine "
        "whether the displayed index set is empty."
    )
    refutation_explanation = (
        "A finite set has a maximum only when it is nonempty. The quote defines "
        "membership using p, the sequence x_n, canonical expansions, and a "
        "digit-prefix predicate, but supplies no values or assumptions that establish "
        "any member exists. Therefore the specific index set cannot be evaluated, "
        "and an abstract empty pattern is not a concrete counterexample to the "
        "source-defined set."
    )
    search_space = (
        "All 512 Boolean membership patterns for the bounded index universe "
        "{0,1,2,3,4,5,6,7,8}, enumerated lexicographically by "
        "itertools.product((False, True), repeat=9). This exhaustive proxy sweep "
        "includes one empty pattern and 511 nonempty patterns, but it is not "
        "exhaustive over the unspecified p, sequence x_n, or expansion predicate."
    )

    pattern_count = 0
    empty_count = 0
    nonempty_count = 0
    for pattern in itertools.product((False, True), repeat=9):
        pattern_count += 1
        members = tuple(index for index, included in enumerate(pattern) if included)
        if members:
            nonempty_count += 1
            candidate_maximum = members[-1]
            assert candidate_maximum in members
            assert all(index <= candidate_maximum for index in members)
        else:
            empty_count += 1

    assert pattern_count == 512
    assert empty_count == 1
    assert nonempty_count == 511

    result = {
        "record_id": "proofwiki_98579__codex_expansion",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": witness_description,
        "refutation_explanation": refutation_explanation,
        "search_space": search_space,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
