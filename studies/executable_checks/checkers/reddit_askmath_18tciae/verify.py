r"""For arbitrary fixed positive ε and δ, one can choose a satisfying ε ≤ a < δ."""

import json

record_id = "reddit_askmath_18tciae"
epsilon = 1
delta = 1

positive_parameters = epsilon > 0 and delta > 0
# In a linear order, epsilon <= a < delta can hold only if epsilon < delta.
interval_is_empty = epsilon >= delta
witness_valid = positive_parameters and interval_is_empty

verdict = "CONFIRMED" if witness_valid else "REFUTED_WITNESS_INVALID"
notes = (
    "Exact arithmetic confirms the witness ε = δ = 1: any a with 1 ≤ a and a < 1 "
    "would imply 1 < 1, a contradiction. The refuted statement is substantive because "
    "it omits the necessary condition ε < δ; it is not plainly a typographical error."
)

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, ensure_ascii=False, separators=(",", ":")))
