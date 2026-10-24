"""Multiplying b > 0 by the negative integer a preserves the inequality and yields ab > 0."""

import json


def main():
    first_witness = None
    pairs_checked = 0

    for a in range(-1, -11, -1):
        for b in range(1, 11):
            pairs_checked += 1
            product = a * b
            if first_witness is None and not (product > 0):
                first_witness = (a, b, product)

    if first_witness is not None and pairs_checked == 100:
        a, b, product = first_witness
        result = {
            "record_id": "reddit_learnmath_20itsx",
            "outcome": "WITNESS_FOUND",
            "witness_description": "a = -1 and b = 1 satisfy that a is a negative integer and b > 0, but ab = -1.",
            "refutation_explanation": "The claimed conclusion ab > 0 is false for this witness because -1 is not greater than 0; multiplying a positive inequality by a negative integer reverses its direction.",
            "search_space": "All 100 ordered integer pairs (a, b) with a in {-1, -2, ..., -10} and b in {1, 2, ..., 10}; every pair was checked in fixed nested-loop order."
        }
    else:
        result = {
            "record_id": "reddit_learnmath_20itsx",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No counterexample was found.",
            "refutation_explanation": "No tested pair violated the claimed conclusion.",
            "search_space": "All 100 ordered integer pairs (a, b) with a in {-1, -2, ..., -10} and b in {1, 2, ..., 10}; every pair was checked in fixed nested-loop order."
        }

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
