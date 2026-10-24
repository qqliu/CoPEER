"""The arbitrary-join calculation claims that φ(∨₁A) = ∧₂φ[A]."""

import json

candidate_instances = ()
found_witness = None
for candidate in candidate_instances:
    found_witness = candidate
    break

assert found_witness is None

result = {
    "record_id": "proofwiki_155440__codex_expansion",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness: the quote supplies no elements, sets, mapping values, orders, or definitions of ∨₁ and ∧₂.",
    "refutation_explanation": "The quote displays the claimed equality and labels it as following from the definition of frame homomorphism, but it provides no fully specified mathematical structure on which either side can be evaluated. Deciding the claim would require inventing absent data.",
    "search_space": "All fully specified candidate instances encoded by the supplied quote: the empty finite set (0 instances), traversed in tuple order."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
