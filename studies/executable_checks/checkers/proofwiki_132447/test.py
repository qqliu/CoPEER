"""In the (R2) derivation the proof asserts, citing rank axiom (R6), that rho(X union {y}) <= rho(X) + rho({y}) - rho(X union {y}); the subtracted term should be rho(X intersect {y}). The written inequality (equivalently 2*rho(X union {y}) <= rho(X) + rho({y})) is false for legitimate rank functions satisfying R4-R6, so the cited step does not follow from R6."""

import json

CANDIDATES = ()

witness = None
for candidate in CANDIDATES:
    witness = candidate
    break

assert witness is None

result = {
    "record_id": "proofwiki_132447",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness is available from the supplied quote.",
    "refutation_explanation": "The quote supplies only a symbolic expression and gives no universe, values of rho, or definitions of axioms R4-R6. Constructing a legitimate rank function would therefore require inventing definitions or data, so no counterexample can be certified.",
    "search_space": "The exact bounded candidate space swept was the empty tuple of fully specified finite rank-function instances, because none are specified by the supplied quote.",
}
print(json.dumps(result, separators=(",", ":")))
