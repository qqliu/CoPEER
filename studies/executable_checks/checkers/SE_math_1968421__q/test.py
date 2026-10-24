"""The resulting graph has $n$ vertices. Apply the inductive hypothesis - this graph has at least $n - 1$ edges."""

import json

RECORD_ID = "SE_math_1968421__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certifiable witness: numerical pairs can violate e >= n - 1, but the "
    "quote does not identify which graphs can be the resulting graph."
)
REFUTATION_EXPLANATION = (
    "The source gives neither the construction producing the resulting graph nor "
    "the inductive hypothesis and its assumptions. Therefore a graph or edge "
    "count violating the displayed inequality cannot be certified as an "
    "admissible resulting graph."
)
SEARCH_SPACE = (
    "Exhaustively swept the 272 ordered integer pairs (n, e) in lexicographic "
    "order with 1 <= n <= 16 and 0 <= e <= 16, checking e < n - 1. This "
    "bounded parameter sweep is illustrative only because admissibility as the "
    "resulting graph is unspecified."
)


def main():
    swept = 0
    numerical_violations = []
    for n in range(1, 17):
        for edge_count in range(0, 17):
            swept += 1
            if edge_count < n - 1:
                numerical_violations.append((n, edge_count))

    assert swept == 272
    assert numerical_violations
    assert numerical_violations[0] == (2, 0)

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
