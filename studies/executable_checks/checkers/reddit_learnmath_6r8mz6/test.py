"""If A ∪ X = B ∪ X, then A = B."""

import itertools
import json

RECORD_ID = "reddit_learnmath_6r8mz6"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "A = ∅, B = {0}, and X = {0}."
REFUTATION_EXPLANATION = (
    "A ∪ X = {0} and B ∪ X = {0}, but A ≠ B, so the implication is false."
)
SEARCH_SPACE = (
    "All 8 ordered triples (A, B, X) where each set is one of the 2 subsets "
    "of the fixed universe {0}; triples are checked in lexicographic bit-mask "
    "order and the entire space is swept."
)


def subset_from_mask(mask):
    return frozenset((0,)) if mask == 1 else frozenset()


def main():
    witnesses = []
    checked = 0
    for a_mask, b_mask, x_mask in itertools.product(range(2), repeat=3):
        a_set = subset_from_mask(a_mask)
        b_set = subset_from_mask(b_mask)
        x_set = subset_from_mask(x_mask)
        checked += 1
        if a_set | x_set == b_set | x_set and a_set != b_set:
            witnesses.append((a_mask, b_mask, x_mask))

    assert checked == 8
    assert witnesses[0] == (0, 1, 1)

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
