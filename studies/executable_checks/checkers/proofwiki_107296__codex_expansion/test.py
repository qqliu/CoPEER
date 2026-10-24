"""The map s_α ↦ α embeds S into the ordinal β defined as the union of the indices used by the construction."""

import itertools
import json


def ordinal_union(indices):
    """Return the exact union of finite von Neumann ordinals."""
    beta = set()
    for alpha in indices:
        beta.update(range(alpha))
    return beta


def main():
    universe = tuple(range(5))
    counterexamples = []

    # Each subset represents S = {s_alpha : alpha is selected}.
    # The entire stated finite search space is swept before reporting.
    for size in range(1, len(universe) + 1):
        for indices in itertools.combinations(universe, size):
            beta = ordinal_union(indices)
            images = tuple(indices)
            injective = len(set(images)) == len(images)
            lands_in_beta = all(alpha in beta for alpha in images)
            if not (injective and lands_in_beta):
                counterexamples.append(indices)

    assert counterexamples
    assert counterexamples[0] == (0,)

    result = {
        "record_id": "proofwiki_107296__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take S = {s_0}. Then the sole index is the finite von Neumann ordinal 0.",
        "refutation_explanation": "For S = {s_0}, beta = union({0}) = 0, the empty ordinal. The proposed image of s_0 is 0, but 0 is not an element of beta = 0. Thus the assignment is not even a map from S into beta, so it cannot be an embedding.",
        "search_space": "All 31 nonempty subsets of the finite ordinal indices {0,1,2,3,4}, swept completely in increasing subset size and lexicographic combination order; beta was computed exactly as the set-theoretic union of the selected finite von Neumann ordinals."
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
