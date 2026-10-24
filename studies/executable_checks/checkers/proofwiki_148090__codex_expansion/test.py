"""The displayed clauses define a functor I_2 from (id_C ↓ C) to (id_C ↓ F)."""

import json

RECORD_ID = "proofwiki_148090__codex_expansion"
CLAIMED_SOURCE = "(id_C ↓ C)"
CLAUSES = (
    ("object clause", "(C ↓ F)"),
    ("morphism clause", "(C ↓ F)"),
)
SEMANTIC_CANDIDATES = ()

mismatches = tuple(
    (clause_name, declared_source)
    for clause_name, declared_source in CLAUSES
    if declared_source != CLAIMED_SOURCE
)
witnesses = tuple(candidate for candidate in SEMANTIC_CANDIDATES)

assert len(CLAUSES) == 2
assert len(mismatches) == 2
assert len(witnesses) == 0

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness is available: the quote supplies no concrete category, functor, object, or morphism interpretation to test.",
    "refutation_explanation": "Both displayed clause headers take their inputs from (C ↓ F), whereas the claimed source is (id_C ↓ C). This is a syntactic typing mismatch, but the supplied data do not provide enough definitions or concrete objects to turn it into a semantic counterexample. Consequently no witness can honestly be certified.",
    "search_space": "Exactly the 2 displayed defining clauses, in quote order: the object clause and the morphism clause. Each clause's single declared input category (C ↓ F) was compared with the single claimed source (id_C ↓ C). The quote supplies 0 concrete semantic interpretations, so 0 object or morphism candidates could be evaluated.",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
