"""The two lexicographically smallest k-faces of an ordered (k+1)-simplex must have the explicit forms stated in the proof of Theorem 2.5."""

import json
from itertools import combinations

RECORD_ID = "arxiv_2301.07191v3__source_enriched_codex"
WITNESS_DESCRIPTION = (
    "k=1 and tau=(0, 1, 2). Its 1-faces, written as increasing vertex "
    "tuples and lexicographically ordered, begin with (0, 1) and (0, 2), "
    "while the quote's displayed formulas give sigma0=(0,) and sigma1=(1,)."
)
REFUTATION_EXPLANATION = (
    "A 1-face of a 2-simplex has two vertices. The displayed sigma0 and "
    "sigma1 each have one vertex (and their union omits 2), so they are not "
    "the two lexicographically smallest 1-faces of tau."
)
SEARCH_SPACE = (
    "All 219 pairs (k, tau) with k in {1,2,3,4,5,6} and tau a strictly "
    "increasing (k+2)-tuple chosen from {0,1,2,3,4,5,6,7}; for each, all "
    "(k+1)-vertex subsets were generated and sorted lexicographically."
)


def displayed_forms(tau, k):
    sigma0 = tuple(tau[:k])
    sigma1 = tuple(tau[: k - 1]) + (tau[k],)
    return sigma0, sigma1


def main():
    first_witness = None
    checked = 0

    for k in range(1, 7):
        for tau in combinations(range(8), k + 2):
            checked += 1
            faces = tuple(sorted(combinations(tau, k + 1)))
            actual_pair = faces[:2]
            stated_pair = displayed_forms(tau, k)
            if actual_pair != stated_pair and first_witness is None:
                first_witness = (k, tau, actual_pair, stated_pair)

    assert checked == 219
    assert first_witness == (
        1,
        (0, 1, 2),
        ((0, 1), (0, 2)),
        ((0,), (1,)),
    )

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
