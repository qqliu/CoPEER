"""For every nonzero Gaussian integer z representing a similarity rotation R of Z[i] by multiplication by z/|z|, the denominator of R with respect to Z[i] equals |z|."""

import itertools
import json

RECORD_ID = "arxiv_2002.07460v3__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "z=1 and z=2: both give multiplication by 1, since "
    "1/|1|=2/|2|=1, but |1|=1 and |2|=2."
)
REFUTATION_EXPLANATION = (
    "The same rotation R cannot have denominator both 1 and 2. Thus the "
    "universal assertion over every nonzero representing z is inconsistent "
    "unless a normalization of z is imposed; none is present in the supplied "
    "claim or quote."
)
SEARCH_SPACE = (
    "All 24 nonzero Gaussian integers a+bi with a,b in {-2,-1,0,1,2}, "
    "and all 276 unordered pairs; exact tests checked positive collinearity "
    "(same normalized rotation) and unequal squared norms."
)

coordinates = tuple(range(-2, 3))
points = tuple(
    (a, b)
    for a, b in itertools.product(coordinates, repeat=2)
    if (a, b) != (0, 0)
)
pairs = tuple(itertools.combinations(points, 2))
violations = []

for first, second in pairs:
    a, b = first
    c, d = second
    determinant = a * d - b * c
    dot_product = a * c + b * d
    first_norm_squared = a * a + b * b
    second_norm_squared = c * c + d * d
    if (
        determinant == 0
        and dot_product > 0
        and first_norm_squared != second_norm_squared
    ):
        violations.append((first, second))

assert len(points) == 24
assert len(pairs) == 276
assert ((1, 0), (2, 0)) in violations

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
