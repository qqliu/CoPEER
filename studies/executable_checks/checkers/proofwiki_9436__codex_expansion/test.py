"""The displayed magnitude bound on an error term implies that its derivative is O(z^{-1})."""

import itertools
import json

RECORD_ID = "proofwiki_9436__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take e(z)=z and c=2. For every complex z with |z|>1, "
    "the displayed two-sided magnitude bound holds."
)
REFUTATION_EXPLANATION = (
    "Since |z^-1|=1/|z|, the displayed upper bound is 2|z|, so "
    "-2|z|<|e(z)|=|z|<2|z|. But e'(z)=1 is not O(z^-1): "
    "for any proposed constants C and R, choosing a real z greater than "
    "both R and C gives 1>C/|z|."
)
SEARCH_SPACE = (
    "All 75 triples (a,k,c) in fixed product order a in (1,-1,2,-2,0), "
    "k in (1,0,-1,-2,2), c in (1,2,3), representing e(z)=a*z^k "
    "on complex |z|>1; each triple was classified symbolically with exact "
    "integer comparisons."
)


def satisfies_displayed_bound(a, k, c):
    """Decide whether |a*z^k| < c/|z^-1| for every |z|>1."""
    if a == 0:
        return True
    magnitude = abs(a)
    if k < 1:
        return magnitude <= c
    if k == 1:
        return magnitude < c
    return False


def derivative_is_not_big_o_inverse_z(a, k):
    """Classify the derivative of a*z^k as |z| tends to infinity."""
    return a != 0 and k > 0


def main():
    coefficients = (1, -1, 2, -2, 0)
    exponents = (1, 0, -1, -2, 2)
    constants = (1, 2, 3)
    witnesses = []

    for a, k, c in itertools.product(coefficients, exponents, constants):
        if satisfies_displayed_bound(a, k, c) and derivative_is_not_big_o_inverse_z(a, k):
            witnesses.append((a, k, c))

    if not witnesses or witnesses[0] != (1, 1, 2):
        raise AssertionError("exact exhaustive classification failed")

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
