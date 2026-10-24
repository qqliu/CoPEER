"""For arbitrary sets A and B and element x, if x∈(A∩B) implies x∈A, then x∈(A∪B)."""

import json
from itertools import combinations


def powerset(universe):
    return tuple(
        frozenset(choice)
        for size in range(len(universe) + 1)
        for choice in combinations(universe, size)
    )


def main():
    universe = (0,)
    subsets = powerset(universe)
    violations = []

    for set_a in subsets:
        for set_b in subsets:
            for element in universe:
                hypothesis = (element not in (set_a & set_b)) or (element in set_a)
                conclusion = element in (set_a | set_b)
                if hypothesis and not conclusion:
                    violations.append((set_a, set_b, element))

    expected = [(frozenset(), frozenset(), 0)]
    assert violations == expected

    result = {
        "record_id": "reddit_learnmath_17xaadi",
        "outcome": "WITNESS_FOUND",
        "witness_description": "In the universe {0}, take A = ∅, B = ∅, and x = 0.",
        "refutation_explanation": "The implication x∈(A∩B) ⇒ x∈A is true vacuously because x∉A∩B, but x∉A∪B, so the claimed conclusion is false.",
        "search_space": "All 4 ordered pairs (A, B) of subsets of the one-element universe {0}, with x = 0; every case was checked in fixed cardinality-then-lexicographic subset order."
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
