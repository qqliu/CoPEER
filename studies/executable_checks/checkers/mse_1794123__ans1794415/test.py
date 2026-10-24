r'''Assuming that the number of men in a family is independent of the number of women in that family, we should expect $\Cov(M, W)$ to be small.  And if we assume that the total number of men is roughly equal to the to the number of women, then $\mathcal M/\mathcal W$ will be roughly equal to $1$.  So women have more brothers if and only if the variance in the number of men per family is less than $\ex M$.'''

import itertools
import json

RECORD_ID = "mse_1794123__ans1794415"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness is reported because the claim's decisive comparison "
    "is not mathematically specified by the supplied quote."
)
REFUTATION_EXPLANATION = (
    "The quote gives no numerical meanings for \"small\" or \"roughly equal,\" "
    "does not define the calligraphic quantities, and does not specify what "
    "comparison is meant by \"women have more brothers.\" Consequently, even "
    "candidate distributions satisfying exact independence and exact equality "
    "of marginal person totals cannot be classified as satisfying or violating "
    "the stated biconditional without inventing definitions."
)
SEARCH_SPACE = (
    "All 19,682 nonzero 3x3 joint-frequency tables with M,W in {0,1,2} and "
    "every table entry in {0,1,2}, visited in itertools.product lexicographic "
    "order; exact integer tests were applied for independence and equality of "
    "the two marginal person totals. This bounded sweep cannot evaluate the "
    "undefined qualitative predicates."
)


def has_exact_independence(table):
    total = sum(table)
    row_sums = tuple(sum(table[3 * m + w] for w in range(3)) for m in range(3))
    column_sums = tuple(sum(table[3 * m + w] for m in range(3)) for w in range(3))
    return all(
        table[3 * m + w] * total == row_sums[m] * column_sums[w]
        for m in range(3)
        for w in range(3)
    )


def has_equal_marginal_person_totals(table):
    men = sum(m * table[3 * m + w] for m in range(3) for w in range(3))
    women = sum(w * table[3 * m + w] for m in range(3) for w in range(3))
    return men == women


def main():
    visited = 0
    exact_premise_candidates = 0
    for table in itertools.product(range(3), repeat=9):
        if not any(table):
            continue
        visited += 1
        if has_exact_independence(table) and has_equal_marginal_person_totals(table):
            exact_premise_candidates += 1

    assert visited == 3 ** 9 - 1
    assert exact_premise_candidates > 0

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
