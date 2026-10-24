r"""The map from the even natural numbers to all two-element sets of natural numbers, defined by n ↦ {n, n+1}, is a bijection."""

import json

record_id = "reddit_askmath_1kehuzl"
notes = "Confirmed exactly: {1, 2} is a two-element set of natural numbers. Any n with {n, n+1} = {1, 2} must equal its minimum element, 1, which is odd; therefore the map is not surjective. The refuted statement is substantive, not plainly a typo."

counterexample = frozenset((1, 2))
is_codomain_member = (
    len(counterexample) == 2
    and all(type(value) is int and value >= 0 for value in counterexample)
)

only_possible_input = min(counterexample)
possible_image = frozenset((only_possible_input, only_possible_input + 1))
has_even_preimage = (
    only_possible_input % 2 == 0
    and possible_image == counterexample
)

verified = is_codomain_member and not has_even_preimage
if not verified:
    raise RuntimeError("independent witness verification failed")

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False))
