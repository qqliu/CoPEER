"""For all complex numbers z1,...,zn, |z1+...+zn|^2 <= |z1|+...+|zn|."""

import itertools
import json

RECORD_ID = "reddit_askmath_i0687v"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "n=1, z1=-2: |-2|^2=4 and |-2|=2."
REFUTATION_EXPLANATION = (
    "The claimed inequality becomes 4 <= 2, which is false; "
    "the real integer -2 is also a complex number."
)
SEARCH_SPACE = (
    "All ordered tuples (z1,...,zn) of real integers (hence complex numbers) "
    "with 1 <= n <= 3 and each zi in {-2,-1,0,1,2}; 155 tuples total, "
    "swept in fixed lexicographic order."
)

values = (-2, -1, 0, 1, 2)
first_witness = None
examined = 0

for n in range(1, 4):
    for zs in itertools.product(values, repeat=n):
        examined += 1
        lhs = sum(zs) ** 2
        rhs = sum(abs(z) for z in zs)
        if lhs > rhs and first_witness is None:
            first_witness = (n, zs, lhs, rhs)

assert examined == 155
assert first_witness == (1, (-2,), 4, 2)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result))
