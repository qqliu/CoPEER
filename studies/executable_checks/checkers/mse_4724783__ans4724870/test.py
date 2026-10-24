r'''There are $\underline{249}$ values of $ 0 \leq n \leq 998$ that satisfy the above condition.'''

import json

RECORD_ID = "mse_4724783__ans4724870"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be named because the referenced \"above condition\" "
    "is absent from the permitted data."
)
REFUTATION_EXPLANATION = (
    "The source quote merely repeats the target claim and never defines the condition "
    "that determines whether an integer n qualifies. Consequently, the qualifying set "
    "and its cardinality cannot be computed or refuted."
)
SEARCH_SPACE = (
    "All 999 integers n in the inclusive interval 0 <= n <= 998 were visited in "
    "increasing order; every one remained unclassifiable because no condition "
    "predicate was supplied."
)


def main():
    visited = []
    for n in range(999):
        visited.append(n)

    assert len(visited) == 999
    assert visited[0] == 0
    assert visited[-1] == 998

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), sort_keys=False))


if __name__ == "__main__":
    main()
