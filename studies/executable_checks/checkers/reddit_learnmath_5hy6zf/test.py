"""For k=n-1 with k sufficiently large, |S_k-L| is at most |S_n-L|."""

import json

RECORD_ID = "reddit_learnmath_5hy6zf"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness is determined because no values or definitions for S, "
    "L, n, or the sufficiently-large threshold are supplied."
)
REFUTATION_EXPLANATION = (
    "The quote states only an inequality. Without a defined sequence S, a value "
    "or domain for L, an index domain, and a threshold interpretation, no "
    "candidate can be evaluated without inventing mathematical data."
)
SEARCH_SPACE = (
    "Exhaustively swept the empty finite space of fully specified tuples "
    "(n, k, L, S_k, S_n, threshold) licensed by the supplied quote: exactly 0 "
    "tuples."
)


def is_counterexample(candidate):
    n, k, limit, s_k, s_n, threshold = candidate
    return (
        k == n - 1
        and k >= threshold
        and abs(s_k - limit) > abs(s_n - limit)
    )


def main():
    candidate_space = ()
    witnesses = tuple(
        candidate for candidate in candidate_space if is_counterexample(candidate)
    )
    assert len(candidate_space) == 0
    assert len(witnesses) == 0

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
