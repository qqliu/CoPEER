"""The final step claims (-1)^k * C(-k, -k-(n-1)) = (-1)^k * C(-k, n-1) by the Symmetry Rule for Binomial Coefficients, but that rule requires a non-negative integer top index; with top index -k < 0 the equality is numerically false (and the intermediate lines are identically 0 whenever n+k >= 2, since their lower index -n-k+1 is negative)."""

import json
from itertools import product


WITNESS_DESCRIPTION = (
    "No counterexample can be certified from the supplied data because neither "
    "the admissible values of n and k nor the meaning of C(a,b) for a negative "
    "top index is defined."
)
REFUTATION_EXPLANATION = (
    "The finite sweep verifies the stated integer-index sign conditions on "
    "positive candidate values, but the truth of the numerical binomial equality "
    "cannot be evaluated without inventing a convention for negative-top "
    "binomial coefficients. Consequently, the sweep cannot establish or refute "
    "the target claim."
)
SEARCH_SPACE = (
    "All 64 ordered integer pairs (n,k) with 1 <= n <= 8 and 1 <= k <= 8, "
    "in lexicographic order with n outermost; for each pair, the conditions "
    "-k < 0 and, when n+k >= 2, -n-k+1 < 0 were checked exactly. No binomial "
    "values were compared because their required negative-top definition is absent."
)


def main():
    checked = 0
    for n, k in product(range(1, 9), range(1, 9)):
        checked += 1
        assert -k < 0
        if n + k >= 2:
            assert -n - k + 1 < 0
    assert checked == 64

    result = {
        "record_id": "proofwiki_49224",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
