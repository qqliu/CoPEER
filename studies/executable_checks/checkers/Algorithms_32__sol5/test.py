"""After moving, this becomes the union of all other components plus vi, which has size n −(previous large component size) −1"""

import json

RECORD_ID = "Algorithms_32__sol5"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified counterexample; the claim is under-specified by the supplied quote."
)
REFUTATION_EXPLANATION = (
    "The quote supplies no definitions of “component,” “moving,” “vi,” the ambient "
    "n-element set, disjointness, or which triples/configurations are admissible. "
    "Consequently, arithmetic assignments with s != n - L - 1 cannot be certified "
    "as instances of the described situation, so the bounded sweep neither refutes "
    "nor verifies the claim."
)
SEARCH_SPACE = (
    "All 284 integer triples (n, L, s) with 1 <= n <= 8 and 0 <= L <= n, "
    "0 <= s <= n, in lexicographic nested-loop order; 36 satisfy "
    "s = n - L - 1 and 248 do not. This is exhaustive only for these bounded "
    "arithmetic placeholders, not for component/move configurations."
)


def main():
    total = 0
    matching = 0
    nonmatching = 0

    for n in range(1, 9):
        for previous_large_size in range(0, n + 1):
            for post_move_size in range(0, n + 1):
                total += 1
                claimed_size = n - previous_large_size - 1
                if post_move_size == claimed_size:
                    matching += 1
                else:
                    nonmatching += 1

    assert total == 284
    assert matching == 36
    assert nonmatching == 248

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
