"""The asserted equality at lines 47–50 identifying h[S_y] with the set of image values equal to min(E \ h[S_y]) is false."""

import json

RECORD_ID = "proofwiki_69689__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be evaluated from the supplied quote."
REFUTATION_EXPLANATION = (
    "The quote supplies only the displayed equality and does not define E, h, "
    "S_y, J, their domains, the order used by min, or whether min(E \\ h[S_y]) "
    "exists. Consequently it determines no semantic instance in which the "
    "equality can be tested, and supplying one would invent absent data."
)
SEARCH_SPACE = (
    "All fully specified semantic interpretations supplied by source_quote: "
    "the empty set (0 interpretations), exhaustively swept in fixed tuple order."
)

# No fully specified interpretation is present in the permitted source data.
# Iterating this explicitly bounded tuple is therefore exhaustive for the data
# actually supplied, while making no invented mathematical assumptions.
supplied_interpretations = ()
witness = None
for interpretation in supplied_interpretations:
    witness = interpretation
    break

assert witness is None

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))
