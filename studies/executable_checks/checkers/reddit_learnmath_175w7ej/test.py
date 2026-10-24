"""From (a - b)^2 = (b - a)^2, taking square roots implies a - b = b - a."""

import json


def main():
    values = range(-2, 3)
    first_witness = None

    for a in values:
        for b in values:
            left_difference = a - b
            right_difference = b - a
            premise = (
                left_difference * left_difference
                == right_difference * right_difference
            )
            conclusion = left_difference == right_difference
            if premise and not conclusion and first_witness is None:
                first_witness = (a, b)

    if first_witness != (-2, -1):
        raise AssertionError("unexpected exhaustive-search result")

    result = {
        "record_id": "reddit_learnmath_175w7ej",
        "outcome": "WITNESS_FOUND",
        "witness_description": "a = -2, b = -1",
        "refutation_explanation": "For a = -2 and b = -1, (a - b)^2 = (-1)^2 = 1 and (b - a)^2 = 1^2 = 1, but a - b = -1 while b - a = 1.",
        "search_space": "All 25 ordered integer pairs (a, b) with a and b in {-2, -1, 0, 1, 2}, checked in lexicographic order; the entire space was swept.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
