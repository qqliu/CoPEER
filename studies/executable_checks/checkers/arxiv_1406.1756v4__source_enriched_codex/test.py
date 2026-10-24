"""For V^k=((x^2+y^2)^2+z^2)^k, the displayed formula for the partial derivative V_y is correct."""

import itertools
import json

RECORD_ID = "arxiv_1406.1756v4__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "At (k,x,y,z)=(2,-1,-1,-1), the actual partial derivative is -80, while the displayed formula evaluates to -64."
REFUTATION_EXPLANATION = "Differentiating V^k gives k*((x^2+y^2)^2+z^2)^(k-1)*(4y^3+4x^2*y). The displayed formula instead uses (x^4+2x^2*y^2+z^2)^(k-1), omitting y^4. At the stated witness its base is 4 rather than 5, so the two values differ."
SEARCH_SPACE = "All 54 tuples with k in {1,2} and x,y,z independently in {-1,0,1}, swept in lexicographic product order; every tuple was checked and the lexicographically first mismatch was reported."


def actual_derivative(k, x, y, z):
    base = (x * x + y * y) ** 2 + z * z
    inner_derivative = 4 * y ** 3 + 4 * x * x * y
    return k * base ** (k - 1) * inner_derivative


def displayed_formula(k, x, y, z):
    displayed_base = x ** 4 + 2 * x * x * y * y + z * z
    inner_derivative = 4 * y ** 3 + 4 * x * x * y
    return k * displayed_base ** (k - 1) * inner_derivative


def main():
    mismatches = []
    for k, x, y, z in itertools.product((1, 2), (-1, 0, 1), (-1, 0, 1), (-1, 0, 1)):
        actual = actual_derivative(k, x, y, z)
        displayed = displayed_formula(k, x, y, z)
        if actual != displayed:
            mismatches.append((k, x, y, z, actual, displayed))

    expected_first = (2, -1, -1, -1, -80, -64)
    if not mismatches or mismatches[0] != expected_first:
        raise AssertionError("deterministic exhaustive search did not recover the stated witness")

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
