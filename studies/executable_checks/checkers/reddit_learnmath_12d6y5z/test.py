"""In case 1, the proof claims that A ∈ F and x ∈ A imply x ∈ ⋂F."""

import json

RECORD_ID = "reddit_learnmath_12d6y5z"
WITNESS_DESCRIPTION = "F = {∅, {0}}, A = {0}, and x = 0."
REFUTATION_EXPLANATION = (
    "A ∈ F and x ∈ A, but ⋂F = ∅ because ∅ ∈ F; therefore x ∉ ⋂F."
)
SEARCH_SPACE = (
    "Universe U = {0, 1}; all 16 families F formed from the 4 subsets of U, "
    "all 4 subsets A of U, and both choices x ∈ U: 128 ordered triples "
    "(F, A, x), swept in increasing bit-mask order."
)


def subset_from_mask(mask, universe):
    return frozenset(
        element for index, element in enumerate(universe) if mask & (1 << index)
    )


def main():
    universe = (0, 1)
    subsets = tuple(subset_from_mask(mask, universe) for mask in range(4))
    first_witness = None

    for family_mask in range(16):
        family = tuple(
            subsets[index]
            for index in range(4)
            if family_mask & (1 << index)
        )
        for a_mask in range(4):
            a_set = subsets[a_mask]
            for x in universe:
                if a_set not in family or x not in a_set:
                    continue
                intersection = set(universe)
                for member in family:
                    intersection.intersection_update(member)
                if x not in intersection and first_witness is None:
                    first_witness = (family_mask, a_mask, x)

    expected_witness = (3, 1, 0)
    if first_witness != expected_witness:
        raise AssertionError("deterministic exhaustive search produced an unexpected result")

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
