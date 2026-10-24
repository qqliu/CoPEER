"""Every LD s_L-code with s>L≥2 contains at most L−1 bad columns, where a bad column is covered by the disjunct sum of floor(s/L) other columns."""

import json

RECORD_ID = "arxiv_1401.0050v6__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness is reported because the supplied text provides no concrete "
    "LD s_L-code instance that can be checked."
)
REFUTATION_EXPLANATION = (
    "The supplied text does not define an LD s_L-code, the column universe, "
    "the disjunct sum operation, or the covering relation. Therefore code "
    "admissibility and badness cannot be evaluated without inventing definitions."
)
SEARCH_SPACE = (
    "The exact finite space swept is the empty tuple () of concrete LD s_L-code "
    "instances explicitly supplied by the target claim and source quote; it has "
    "cardinality 0."
)

CHECKABLE_INSTANCES = ()
for candidate in CHECKABLE_INSTANCES:
    raise AssertionError("The declared search space must be empty")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
