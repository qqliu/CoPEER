r"""For every x ∈ A, there exists some a ∈ x (and hence a ∈ ∪A)."""

import json

record_id = "reddit_askmath_11gn0pk"
notes = "Independent exact recomputation confirms the witness: with A = {∅} and x = ∅, x ∈ A, ∪A = ∅, and no a ∈ x exists. The refuted statement is substantively false without a nonemptiness assumption, not plainly a typo."

x = frozenset()
A = frozenset((x,))
union_A = frozenset(element for member in A for element in member)
x_is_member = x in A
required_element_exists = any(element in x and element in union_A for element in x)
claim_holds_for_A = all(any(element in member and element in union_A for element in member) for member in A)
witness_is_valid = x_is_member and union_A == frozenset() and not required_element_exists and not claim_holds_for_A
verdict = "CONFIRMED" if witness_is_valid else "REFUTED_WITNESS_INVALID"

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False))
