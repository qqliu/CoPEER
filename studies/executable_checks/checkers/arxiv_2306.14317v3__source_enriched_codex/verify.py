"""Every even-dimensional finite-field vector space equipped with a quadratic form whose associated bilinear form is nondegenerate decomposes into mutually orthogonal hyperbolic pairs."""

import json

record_id = "arxiv_2306.14317v3__source_enriched_codex"
prime = 3
vectors = [(x, y) for x in range(prime) for y in range(prime)]
zero = (0, 0)


def q(vector):
    x, y = vector
    return (x * x + y * y) % prime


def add(left, right):
    return ((left[0] + right[0]) % prime, (left[1] + right[1]) % prime)


def bilinear(left, right):
    return (q(add(left, right)) - q(left) - q(right)) % prime


radical = []
for candidate in vectors:
    if all(bilinear(candidate, test) == 0 for test in vectors):
        radical.append(candidate)

nonzero_isotropic = [vector for vector in vectors if vector != zero and q(vector) == 0]
even_dimension = 2 % 2 == 0
nondegenerate = radical == [zero]
no_hyperbolic_pair = len(nonzero_isotropic) == 0
verified = even_dimension and nondegenerate and no_hyperbolic_pair

if verified:
    verdict = "CONFIRMED"
    notes = "Exact recomputation over F_3 verifies that q(x,y)=x^2+y^2 has a nondegenerate polarized bilinear form and no nonzero isotropic vector, so it cannot contain the required hyperbolic pair. The refuted statement is substantive, not plainly a typo; it omits a split/hyperbolic hypothesis."
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "Exact recomputation did not establish the reported witness."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
