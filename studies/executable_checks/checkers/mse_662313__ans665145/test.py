"""Since $e$ and $f$ are coprime, so are the three factors $2e$, $e+f$, and $e−f$; therefore, they are each the cube of smaller integers, $k$, $l$, and $m$."""

import json
from math import gcd

RECORD_ID = "mse_662313__ans665145"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "e=3 and f=1: gcd(e,f)=1, but the three factors are 6, 4, and 2."
)
REFUTATION_EXPLANATION = (
    "The factors are not coprime: gcd(6,4)=gcd(6,2)=gcd(4,2)=2. "
    "Thus coprimality of e and f does not imply the asserted coprimality "
    "of 2e, e+f, and e−f."
)
SEARCH_SPACE = (
    "All 28 ordered positive-integer pairs (e,f) satisfying 1 <= f < e <= 8, "
    "in increasing e then increasing f order; every pair was swept, and pairs "
    "with gcd(e,f)=1 were checked for pairwise coprimality of 2e, e+f, and e−f."
)

first_witness = None
pairs_swept = 0
for e in range(1, 9):
    for f in range(1, e):
        pairs_swept += 1
        if gcd(e, f) != 1:
            continue
        factors = (2 * e, e + f, e - f)
        pair_gcds = (
            gcd(abs(factors[0]), abs(factors[1])),
            gcd(abs(factors[0]), abs(factors[2])),
            gcd(abs(factors[1]), abs(factors[2])),
        )
        if first_witness is None and pair_gcds != (1, 1, 1):
            first_witness = (e, f, factors, pair_gcds)

assert pairs_swept == 28
assert first_witness == (3, 1, (6, 4, 2), (2, 2, 2))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
