"""If Σ(k≥1)|aₖ|=L and g:ℕ→ℕ is a bijection, then Σ(k≥1)a_{g(k)}=L."""

import json
from itertools import permutations, product

RECORD_ID = "reddit_askmath_1837jgc"
WITNESS_DESCRIPTION = (
    "Let a₁=-1 and aₖ=0 for every k≥2, let L=1, and let g(k)=k on ℕ."
)
REFUTATION_EXPLANATION = (
    "Then Σ(k≥1)|aₖ|=1=L, but Σ(k≥1)a_{g(k)}=-1≠1, "
    "so the claimed conclusion fails even for the identity bijection."
)
SEARCH_SPACE = (
    "All 3 sequences supported on {1} with a₁∈{-1,0,1} and aₖ=0 for k≥2, "
    "paired with the sole permutation of {1} extended as the identity for k≥2; "
    "all 3 pairs were checked in the fixed order a₁=-1,0,1."
)

first_witness = None
checked = 0
for coefficients in product((-1, 0, 1), repeat=1):
    for permutation in permutations((1,)):
        checked += 1
        absolute_sum = sum(abs(value) for value in coefficients)
        rearranged_sum = sum(coefficients[index - 1] for index in permutation)
        if rearranged_sum != absolute_sum and first_witness is None:
            first_witness = (coefficients, permutation, absolute_sum, rearranged_sum)

assert checked == 3
assert first_witness == ((-1,), (1,), 1, -1)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
