"""Every complete lattice is an object of Frm, so CLat is a subcategory of Frm."""

import json

RECORD_ID = "proofwiki_144841__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete candidate mathematical structure is supplied by the permitted "
    "source data, so no witness can be tested without inventing absent definitions "
    "or data."
)
REFUTATION_EXPLANATION = (
    "The quote asserts a subcollection relationship but does not define complete "
    "lattices, Frm objects, frame homomorphisms, or subcategories, and it supplies "
    "no candidate structure. Therefore the claim is not decidable from the "
    "permitted data by a non-invented finite counterexample test."
)
SEARCH_SPACE = (
    "Exactly the empty tuple of candidate mathematical structures supplied "
    "explicitly by the source quote (0 candidates); all 0 candidates were examined "
    "in fixed tuple order."
)

candidates = ()
for candidate in candidates:
    raise AssertionError("The explicitly supplied candidate space must be empty")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":"), sort_keys=False))
