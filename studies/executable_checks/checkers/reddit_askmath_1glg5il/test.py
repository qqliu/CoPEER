"""For all sets A, B, and C, A - (B - C) = (A - C) ∪ (A ∩ B)."""

import itertools
import json


def subset_from_mask(mask):
    return frozenset({0}) if mask == 1 else frozenset()


def main():
    failures = []
    for a_mask, b_mask, c_mask in itertools.product(range(2), repeat=3):
        a_set = subset_from_mask(a_mask)
        b_set = subset_from_mask(b_mask)
        c_set = subset_from_mask(c_mask)
        left = a_set.difference(b_set.difference(c_set))
        right = a_set.difference(c_set).union(a_set.intersection(b_set))
        if left != right:
            failures.append((a_mask, b_mask, c_mask))

    if not failures or failures[0] != (1, 0, 1):
        raise AssertionError("exhaustive search did not find the expected witness")

    result = {
        "record_id": "reddit_askmath_1glg5il",
        "outcome": "WITNESS_FOUND",
        "witness_description": "A = {0}, B = empty set, and C = {0}.",
        "refutation_explanation": "Here B - C is empty, so A - (B - C) = {0}. But A - C and A intersection B are both empty, so the right-hand side is empty. Therefore the two sides are unequal.",
        "search_space": "All 8 ordered triples (A, B, C) in which each set is a subset of the fixed singleton universe {0}; every triple was checked in lexicographic bit-mask order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
