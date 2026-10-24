r'''For a mapping represented by graph R, the value f(a) is defined as the inverse image R^{-1}({a}).'''

import json

record_id = "reddit_learnmath_b5iobo"
domain = frozenset((0, 1))
codomain = frozenset((0, 1))
relation = frozenset(((0, 0), (1, 0)))
a = 0

assert all(x in domain and y in codomain for x, y in relation)
assert all(sum(1 for x, y in relation if x == argument) == 1 for argument in domain)

values_at_a = frozenset(y for x, y in relation if x == a)
assert len(values_at_a) == 1
value_at_a = next(iter(values_at_a))
inverse_image = frozenset(x for x, y in relation if y in frozenset((a,)))

assert value_at_a == 0
assert inverse_image == frozenset((0, 1))
assert frozenset((value_at_a,)) != inverse_image
assert value_at_a != inverse_image

payload = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms the witness: for the constant-zero function on {0,1} at a=0, f(a)=0 but the inverse image of {a} is {0,1}; even {f(a)}={0} is different. The refuted statement is substantive, not plainly a typo.",
}
print(json.dumps(payload, separators=(",", ":")))
