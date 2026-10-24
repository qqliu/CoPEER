"""The asserted equality |max(f(s),g(s))| = |max(|f(s)|,|g(s)|)| is false in general."""

import itertools
import json


def main():
    values = (-2, -1, 0, 1, 2)
    violations = []
    for f_value, g_value in itertools.product(values, repeat=2):
        left = abs(max(f_value, g_value))
        right = abs(max(abs(f_value), abs(g_value)))
        if left != right:
            violations.append((f_value, g_value, left, right))

    witness = violations[0]
    assert witness == (-2, -1, 1, 2)

    result = {
        "record_id": "proofwiki_123738__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take a point s with f(s) = -2 and g(s) = -1.",
        "refutation_explanation": "For this witness, |max(f(s), g(s))| = |max(-2, -1)| = 1, while |max(|f(s)|, |g(s)|)| = |max(2, 1)| = 2. Since 1 != 2, the asserted equality fails.",
        "search_space": "All 25 ordered integer pairs (f(s), g(s)) in {-2, -1, 0, 1, 2}^2, checked in lexicographic order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
