"""For λ = ⌈(n−1)/2⌉, 2λ is always the largest even number in {1,2,…,n+1}."""

import json

RECORD_ID = "arxiv_0910.0923v4__source_enriched_codex"
WITNESS_DESCRIPTION = (
    "n = 3 is a counterexample: λ = 1 and 2λ = 2, but the largest even "
    "number in {1,2,3,4} is 4."
)
REFUTATION_EXPLANATION = (
    "For n = 3, λ = ⌈(3−1)/2⌉ = 1. Hence 2λ = 2, whereas n+1 = 4 is "
    "even and belongs to {1,2,…,n+1}, so 2λ is not the largest even "
    "number in that set."
)
SEARCH_SPACE = (
    "All integer n from 2 through 64 inclusive were checked in increasing "
    "order using exact integer arithmetic; every even member of "
    "{1,2,…,n+1} was enumerated for each n."
)


def ceil_div(a, b):
    return -((-a) // b)


def main():
    counterexamples = []
    for n in range(2, 65):
        lam = ceil_div(n - 1, 2)
        even_members = tuple(x for x in range(1, n + 2) if x % 2 == 0)
        largest_even = max(even_members)
        if 2 * lam != largest_even:
            counterexamples.append((n, lam, 2 * lam, largest_even))

    if not counterexamples or counterexamples[0] != (3, 1, 2, 4):
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
