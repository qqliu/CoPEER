"""From x∈A and x∉C, it follows that A∩C=∅."""

import json


def subset_from_mask(mask, universe):
    return frozenset(
        universe[index]
        for index in range(len(universe))
        if mask & (1 << index)
    )


def main():
    universe = (0, 1)
    first_witness = None

    for x in universe:
        for a_mask in range(1 << len(universe)):
            a_set = subset_from_mask(a_mask, universe)
            for c_mask in range(1 << len(universe)):
                c_set = subset_from_mask(c_mask, universe)
                if x in a_set and x not in c_set and a_set.intersection(c_set):
                    if first_witness is None:
                        first_witness = (x, a_set, c_set)

    expected = (0, frozenset((0, 1)), frozenset((1,)))
    if first_witness != expected:
        raise AssertionError("deterministic exhaustive search returned an unexpected result")

    result = {
        "record_id": "reddit_learnmath_hk1eur",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Let x=0, A={0, 1}, and C={1}. Then 0 is in A and 0 is not in C, while A intersect C={1}.",
        "refutation_explanation": "The premises concern only x: they do not prevent a different element, here 1, from belonging to both A and C. Thus the intersection is nonempty, contradicting the claimed conclusion.",
        "search_space": "All 32 ordered triples (x, A, C), where x is in the fixed universe {0, 1} and A and C independently range over all four subsets of that universe, were checked in fixed lexicographic mask order."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
