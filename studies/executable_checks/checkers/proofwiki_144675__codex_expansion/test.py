"""For every subset X of A, id_A(sup A) equals sup{id_A(x) : x in X}."""

import itertools
import json

RECORD_ID = "proofwiki_144675__codex_expansion"
WITNESS_DESCRIPTION = (
    "In the two-element chain A={0,1} with id_A(x)=x and suprema given by "
    "maxima, take X={0}; id_A(sup A)=1 while "
    "sup{id_A(x) : x in X}=0."
)
REFUTATION_EXPLANATION = (
    "The claim quantifies over every subset X of A, so the concrete nonempty "
    "subset X={0} suffices to refute it: the asserted equality reads 1=0."
)
SEARCH_SPACE = (
    "All 26 nonempty subsets of the four finite chains A_n={0,...,n-1} for "
    "n=1,2,3,4, with id_A the identity and each nonempty supremum computed "
    "as the maximum; the entire bounded space is swept in increasing n, "
    "subset size, and lexicographic order."
)


def identity(value):
    return value


def main():
    first_witness = None
    subsets_checked = 0

    for size in range(1, 5):
        universe = tuple(range(size))
        left = identity(max(universe))
        for subset_size in range(1, size + 1):
            for subset in itertools.combinations(universe, subset_size):
                subsets_checked += 1
                right = max(identity(value) for value in subset)
                if left != right and first_witness is None:
                    first_witness = (universe, subset, left, right)

    assert subsets_checked == 26
    assert first_witness == ((0, 1), (0,), 1, 0)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
