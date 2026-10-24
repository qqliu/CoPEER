"""The proof claims that -log² N + log N - 3 is positive for every N > e⁴."""

import json

RECORD_ID = "reddit_mathematics_1okpgze"
WITNESS_DESCRIPTION = "N = e^5. Then N > e^4 and log N = 5."
REFUTATION_EXPLANATION = (
    "At N = e^5, -log² N + log N - 3 = -(5^2) + 5 - 3 = -23, "
    "which is not positive."
)
SEARCH_SPACE = (
    "All symbolic candidates N = e^k for integer k in [5, 5] "
    "(exactly the singleton {e^5})."
)


def search():
    for k in range(5, 6):
        is_above_threshold = k > 4
        value = -(k * k) + k - 3
        if is_above_threshold and value <= 0:
            return "WITNESS_FOUND"
    return "NO_WITNESS_EXHAUSTIVE"


result = {
    "record_id": RECORD_ID,
    "outcome": search(),
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
