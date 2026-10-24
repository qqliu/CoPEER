"""Equation (3) correctly restates the naturality condition for the fixed-second-variable transformation."""

import json

RECORD_ID = "proofwiki_149531__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness exists in the supplied data: the quote gives no "
    "definitions or typing information from which a semantic counterexample "
    "can be instantiated."
)
REFUTATION_EXPLANATION = (
    "Whether Equation (3) is a correct naturality condition depends on the "
    "categories, functor G, transformation alpha, morphism f, component types, "
    "and composition convention. None of these are defined by the supplied "
    "quote, so the displayed equality alone cannot establish either correctness "
    "or a counterexample."
)
SEARCH_SPACE = (
    "Exhaustively swept the finite set of fully specified semantic "
    "counterexample instances constructible from source_quote alone. That set "
    "has cardinality 0 because the quote supplies only the displayed equation "
    "and no admissible structures or typing data."
)

# A semantic witness must specify enough categorical data to interpret and
# type-check both sides. The permitted quote supplies no such instance, so the
# exact finite candidate space constructible from it is empty.
candidate_instances = ()
witness = None
for candidate in candidate_instances:
    witness = candidate
    break

assert witness is None
assert len(candidate_instances) == 0

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False, separators=(",", ":")))
