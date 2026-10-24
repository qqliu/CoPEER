"""For arbitrary sets A and B and element x, if x∈(A∩B) implies x∈A, then x∈(A∪B)."""

import json

record_id = "reddit_learnmath_17xaadi"
set_a = frozenset()
set_b = frozenset()
element = 0

premise_left = element in set_a.intersection(set_b)
premise_right = element in set_a
inner_implication = (not premise_left) or premise_right
conclusion = element in set_a.union(set_b)
witness_refutes_claim = inner_implication and not conclusion

if witness_refutes_claim:
    verdict = "CONFIRMED"
    notes = "Exact recomputation confirms the witness: with A = ∅, B = ∅, and x = 0, the inner implication is vacuously true while x ∉ A ∪ B. The refuted statement is a substantive logical error, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact recomputation does not validate the reported witness. The refuted statement would be substantive rather than plainly a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False))
