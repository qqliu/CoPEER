r"""The proof claims that X ∉ A ∩ B implies X ∈ A △ B."""

import json

record_id = "reddit_learnmath_918alc"
x = "X"
universe = frozenset((x,))
a = frozenset()
b = frozenset()

intersection = a.intersection(b)
symmetric_difference = a.symmetric_difference(b)
antecedent = x not in intersection
consequent = x in symmetric_difference
witness_is_valid = (
    a.issubset(universe)
    and b.issubset(universe)
    and antecedent
    and not consequent
)

if witness_is_valid:
    verdict = "CONFIRMED"
    notes = "Exact set arithmetic confirms the witness A = ∅ and B = ∅: X is not in A ∩ B, while X is also not in A △ B, so the implication fails. The refuted statement is a substantive logical error, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The reported witness does not refute the claim. The statement would represent a substantive logical assertion rather than a plainly identifiable typo."

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, ensure_ascii=False, separators=(",", ":")))
