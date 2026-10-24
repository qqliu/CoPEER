"""Multiplying any edge of the minimum-size important (X,Y)-cut strictly increases the minimum important-cut size."""

import json

RECORD_ID = "arxiv_2201.12790v2__source_enriched_codex"
TARGET_CLAIM = "Multiplying any edge of the minimum-size important (X,Y)-cut strictly increases the minimum important-cut size."
SOURCE_QUOTE = "Multiplication of any edge in the minimum-size important $(X,Y)$-cut of $G$ increases the size of minimum important $(X,Y)$-cut in $G$."
SUPPLIED_RECORDS = ((TARGET_CLAIM, SOURCE_QUOTE),)
CANDIDATES = ()

for _candidate in CANDIDATES:
    raise AssertionError("No mathematical candidates are specified by the supplied data")

assert len(SUPPLIED_RECORDS) == 1
assert len(CANDIDATES) == 0

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be named from the supplied data.",
    "refutation_explanation": "The quote supplies no graph instance and does not define an important cut, edge multiplication, or cut size. Therefore no candidate can be evaluated without inventing definitions or data.",
    "search_space": "Exactly the singleton containing the supplied (target_claim, source_quote) pair was inspected; it specifies zero graph instances, so zero mathematical candidates were evaluable.",
}
print(json.dumps(result, separators=(",", ":")))
