"""The stated subset P has a smallest element merely because the ambient set is well-ordered."""

import itertools
import json

RECORD_ID = "proofwiki_69637__codex_expansion"
WITNESS_DESCRIPTION = (
    "P = ∅. The empty set satisfies the displayed subset condition because it is "
    "a subset of every set, but it has no element and therefore no smallest element."
)
REFUTATION_EXPLANATION = (
    "Well-ordering guarantees a smallest element only for nonempty subsets. The "
    "quote does not state that P is nonempty, so choosing P = ∅ directly violates "
    "the claimed conclusion even if the ambient set is well-ordered."
)
SEARCH_SPACE = (
    "All subsets P of the zero-element candidate universe: exactly {∅} (1 candidate), "
    "enumerated in increasing subset-size and lexicographic combination order."
)


def subsets(items):
    for size in range(len(items) + 1):
        for choice in itertools.combinations(items, size):
            yield choice


def main():
    witness_found = False
    candidate_universe = ()

    for p in subsets(candidate_universe):
        satisfies_displayed_inclusion = len(p) == 0
        has_smallest_element = len(p) != 0
        if satisfies_displayed_inclusion and not has_smallest_element:
            witness_found = True
            break

    if witness_found:
        result = {
            "record_id": RECORD_ID,
            "outcome": "WITNESS_FOUND",
            "witness_description": WITNESS_DESCRIPTION,
            "refutation_explanation": REFUTATION_EXPLANATION,
            "search_space": SEARCH_SPACE,
        }
    else:
        result = {
            "record_id": RECORD_ID,
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": WITNESS_DESCRIPTION,
            "refutation_explanation": REFUTATION_EXPLANATION,
            "search_space": SEARCH_SPACE,
        }

    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
