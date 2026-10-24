"""The proof claims that |min(f(s),g(s))| = |min(|f(s)|,|g(s)|)|."""

import itertools
import json

RECORD_ID = "proofwiki_123739__codex_expansion"
VALUES = (-2, -1, 0, 1, 2)
SEARCH_SPACE = (
    "All 25 ordered integer pairs (x, y) in {-2, -1, 0, 1, 2}^2, "
    "in lexicographic product order; every pair was evaluated exactly once."
)

counterexamples = []
checked = 0
for x, y in itertools.product(VALUES, repeat=2):
    checked += 1
    left = abs(min(x, y))
    right = abs(min(abs(x), abs(y)))
    if left != right:
        counterexamples.append((x, y, left, right))

assert checked == 25

if counterexamples:
    x, y, left, right = counterexamples[0]
    assert (x, y, left, right) == (-2, -1, 2, 1)
    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": (
            "Let f(s) = -2 and g(s) = -1. Then |min(f(s),g(s))| = 2, "
            "but |min(|f(s)|,|g(s)|)| = 1."
        ),
        "refutation_explanation": (
            "With x = f(s) = -2 and y = g(s) = -1, the left side is "
            "abs(min(-2,-1)) = 2, while the right side is "
            "abs(min(abs(-2),abs(-1))) = 1. Since 2 != 1, the claimed "
            "equality fails."
        ),
        "search_space": SEARCH_SPACE,
    }
else:
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "No counterexample was found in the bounded space.",
        "refutation_explanation": "The bounded search found no unequal pair.",
        "search_space": SEARCH_SPACE,
    }

print(json.dumps(result, sort_keys=True, separators=(",", ":")))
