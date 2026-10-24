"""In Case 1, the condition x ∈ A implies F(A ∪ B) = F(A)."""

import json
from itertools import product


def image(subset, mapping):
    return {mapping[element] for element in subset}


def main():
    universe = (0, 1)
    subsets = tuple(
        tuple(element for element in universe if mask & (1 << element))
        for mask in range(4)
    )

    first_witness = None
    examined = 0
    for a_set in subsets:
        for b_set in subsets:
            for mapping in product(universe, repeat=2):
                for x in universe:
                    examined += 1
                    union = tuple(sorted(set(a_set) | set(b_set)))
                    if x in a_set and image(union, mapping) != image(a_set, mapping):
                        if first_witness is None:
                            first_witness = (a_set, b_set, mapping, x)

    assert examined == 128
    assert first_witness == ((0,), (1,), (0, 1), 0)

    result = {
        "record_id": "reddit_askmath_1m7i8q3",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Let X = Y = {0, 1}, A = {0}, B = {1}, x = 0, and F be the identity function: F(0) = 0 and F(1) = 1.",
        "refutation_explanation": "Here x ∈ A, but F(A ∪ B) = {0, 1}, whereas F(A) = {0}. Thus the asserted equality does not follow from x ∈ A.",
        "search_space": "All 128 tuples (A, B, F, x), where A and B range over all 4 subsets of {0, 1}, F ranges over all 4 total functions from {0, 1} to {0, 1}, and x ranges over {0, 1}, swept in fixed lexicographic numeric order."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
