"""you'll actually need all those cases with $n=0$ and arbitrary $m$, and all the cases with $m=1$ and arbitrary $n$, as your base cases, so that you can go from the $(m-1,n)$ and the $(m,n)$ case to the $(m+1,n)$ case, and from the $(m,n-1)$ and the $(m,n)$ case to the $(m,n+1)$ case."""

import itertools
import json

RECORD_ID = "mse_2662707__ans2662794"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness is identifiable because neither a mathematical "
    "predicate for a “case” nor a derivability relation is supplied."
)
REFUTATION_EXPLANATION = (
    "The quote asserts that certain base cases are needed, but it does not "
    "define the statement indexed by (m,n), the domains of m and n, or the "
    "inference rules denoted by “go from.” Consequently, every candidate pair "
    "in the bounded sweep is undecidable from the permitted data, so the sweep "
    "cannot establish or refute the claimed necessity."
)
SEARCH_SPACE = (
    "All 289 ordered integer pairs (m,n) with -8 <= m <= 8 and -8 <= n <= 8, "
    "visited in lexicographic order. Each pair was checked for an evaluable "
    "case predicate and inference relation supplied by the quote; none exists. "
    "This is an illustrative bounded sweep, not an exhaustive test of arbitrary "
    "m and n."
)


def evaluate_candidate(m, n):
    # The source assigns no truth value to any indexed case and supplies no
    # formal inference relation. Returning None records that the candidate is
    # undecidable without adding definitions absent from the source.
    if isinstance(m, int) and isinstance(n, int):
        return None
    raise AssertionError("The fixed search space contains only integer pairs")


def main():
    checked = 0
    for m, n in itertools.product(range(-8, 9), repeat=2):
        checked += 1
        verdict = evaluate_candidate(m, n)
        if verdict is False:
            raise AssertionError("An evaluator without a supplied predicate cannot refute")

    if checked != 289:
        raise AssertionError("The declared bounded space was not fully swept")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=False))


if __name__ == "__main__":
    main()
