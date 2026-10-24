"""Every strictly increasing function f: R → R has an inverse f⁻¹: R → R."""

import json

RECORD_ID = "reddit_learnmath_mjbxwz"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let f(x) = x - 2 for x < 0 and f(x) = x - 1 for x >= 0. "
    "This function is strictly increasing on R, but -2 is not in its image."
)
REFUTATION_EXPLANATION = (
    "On either side of 0, f preserves strict order. If x < 0 <= y, then "
    "f(x) < -2 < -1 <= f(y), so f is strictly increasing across the breakpoint "
    "as well. Its image is (-infinity, -2) union [-1, infinity), so no real "
    "input maps to -2. Therefore f cannot have an inverse whose domain is all of R."
)
SEARCH_SPACE = (
    "All 25 integer pairs (a, b) in {-2, -1, 0, 1, 2}^2 were checked in "
    "lexicographic order for the piecewise translations f_{a,b}(x) = x + a "
    "when x < 0 and f_{a,b}(x) = x + b when x >= 0. For this family, strict "
    "increase is certified exactly by a <= b, and when a < b the value a is "
    "certified absent from the image."
)


def main():
    values = range(-2, 3)
    checked = []
    counterexamples = []

    for a in values:
        for b in values:
            checked.append((a, b))
            strictly_increasing = a <= b
            omitted_value_certified = a < b
            if strictly_increasing and omitted_value_certified:
                counterexamples.append((a, b, a))

    assert len(checked) == 25
    assert counterexamples[0] == (-2, -1, -2)

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
