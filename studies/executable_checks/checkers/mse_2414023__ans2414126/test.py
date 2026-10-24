"""If $f(1)=3$, then $P(1)$ gives $f(3)=1$.  Then, $P(3)$, $P(4)$, and $P(5)$ yield $f(4)=5$, $f(5)=4$, and $f(6)=5$, respectively."""

import itertools
import json


RECORD_ID = "mse_2414023__ans2414126"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified counterexample: the sweep finds raw tables with f(1)=3 "
    "that violate one or more listed equalities, but the quote does not "
    "define P(n) or the admissible functions f."
)
REFUTATION_EXPLANATION = (
    "A violating table can be certified only if it also satisfies whatever "
    "hypotheses P(1), P(3), P(4), and P(5) express. Since P is undefined in "
    "the supplied data, finite assignments to the displayed values of f "
    "cannot determine admissibility, so the search is inconclusive."
)
SEARCH_SPACE = (
    "Exhaustively swept all 6^5 = 7776 tables assigning f(1), f(3), f(4), "
    "f(5), and f(6) values from {1,2,3,4,5,6}, in lexicographic "
    "itertools.product order; 1295 tables have f(1)=3 and violate at least "
    "one listed consequent equality. This sweep is exhaustive only for "
    "those raw tables, not for the undefined P constraints or the claim."
)


def main():
    values = range(1, 7)
    expected = (1, 5, 4, 5)
    tables_examined = 0
    raw_violations = 0

    for table in itertools.product(values, repeat=5):
        tables_examined += 1
        f1, f3, f4, f5, f6 = table
        if f1 == 3 and (f3, f4, f5, f6) != expected:
            raw_violations += 1

    assert tables_examined == 7776
    assert raw_violations == 1295

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
