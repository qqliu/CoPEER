"""The displayed equality chain for x + y is valid for arbitrary integers k and j, including the step that replaces 2j by 2k."""

import itertools
import json


def main():
    values = range(-2, 3)
    violations = []

    for k, j in itertools.product(values, repeat=2):
        original_sum = (2 * k + 1) + (2 * j + 1)
        replaced_sum = 2 * k + 2 * k + 2
        if original_sum != replaced_sum:
            violations.append((k, j, original_sum, replaced_sum))

    assert len(violations) > 0
    assert violations[0] == (-2, -1, -4, -6)

    result = {
        "record_id": "reddit_learnmath_18emvdx",
        "outcome": "WITNESS_FOUND",
        "witness_description": "k = -2 and j = -1. Then (2k + 1) + (2j + 1) = -4, while 2k + 2k + 2 = -6.",
        "refutation_explanation": "The step replacing 2j by 2k requires j = k. For the swept pair k = -2, j = -1, the two sides differ, so the displayed equality chain is not valid for arbitrary integers.",
        "search_space": "All 25 ordered integer pairs (k, j) with k and j each in {-2, -1, 0, 1, 2}, checked in lexicographic product order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
