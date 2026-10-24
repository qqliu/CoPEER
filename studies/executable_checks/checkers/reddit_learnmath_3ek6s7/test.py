"""For every point p outside E', there exists a neighborhood of p containing no point of E and no point of E'."""

import json

RECORD_ID = "reddit_learnmath_3ek6s7"
CANDIDATE_CONFIGURATIONS = ()

witness = None
for candidate in CANDIDATE_CONFIGURATIONS:
    witness = candidate
    break

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be formed from the supplied data.",
    "refutation_explanation": "The quote merely restates the claim and supplies no universe of points, interpretations of E and E', or neighborhood system. Therefore it does not determine whether any point violates the claim.",
    "search_space": "The explicitly bounded space is the empty tuple of concrete configurations supplied by the quote: exactly 0 configurations were swept.",
}
print(json.dumps(result, separators=(",", ":")))
