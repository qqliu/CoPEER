"""Every even-dimensional finite-field vector space equipped with a quadratic form whose associated bilinear form is nondegenerate decomposes into mutually orthogonal hyperbolic pairs."""

import json
from itertools import product

RECORD_ID = "arxiv_2306.14317v3__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Take V = F_3^2 and q(x,y) = x^2 + y^2. Its polarized bilinear form has matrix diag(2,2), whose determinant is 1 modulo 3, so it is nondegenerate."
REFUTATION_EXPLANATION = "The only vector with q(x,y)=0 is (0,0): a nonzero coordinate has square 1 modulo 3, so q is 1 when exactly one coordinate is nonzero and 2 when both are nonzero. Thus V has no nonzero isotropic vector and hence no hyperbolic pair, while dimension 2 would require one hyperbolic pair."
SEARCH_SPACE = "All 27 coefficient triples (a,b,c) in F_3^3 defining q(x,y)=a*x^2+b*x*y+c*y^2 on F_3^2 were swept in lexicographic order. For every form, nondegeneracy was checked against all 9 possible kernel vectors and all 9 test vectors, and all 81 ordered vector pairs were checked for an isotropic, linearly independent pair with nonzero polarized pairing."

P = 3
VECTORS = tuple(product(range(P), repeat=2))
COEFFICIENTS = tuple(product(range(P), repeat=3))
ORDERED_PAIRS = tuple(product(VECTORS, repeat=2))
ZERO = (0, 0)


def quadratic(coefficients, vector):
    a, b, c = coefficients
    x, y = vector
    return (a * x * x + b * x * y + c * y * y) % P


def polarized(coefficients, left, right):
    summed = ((left[0] + right[0]) % P, (left[1] + right[1]) % P)
    return (
        quadratic(coefficients, summed)
        - quadratic(coefficients, left)
        - quadratic(coefficients, right)
    ) % P


def is_nondegenerate(coefficients):
    for left in VECTORS:
        if left != ZERO and all(
            polarized(coefficients, left, right) == 0 for right in VECTORS
        ):
            return False
    return True


def is_hyperbolic_pair(coefficients, left, right):
    determinant = (left[0] * right[1] - left[1] * right[0]) % P
    return (
        quadratic(coefficients, left) == 0
        and quadratic(coefficients, right) == 0
        and determinant != 0
        and polarized(coefficients, left, right) != 0
    )


def main():
    counterexamples = []
    for coefficients in COEFFICIENTS:
        nondegenerate = is_nondegenerate(coefficients)
        has_hyperbolic_pair = False
        for left, right in ORDERED_PAIRS:
            if is_hyperbolic_pair(coefficients, left, right):
                has_hyperbolic_pair = True
        if nondegenerate and not has_hyperbolic_pair:
            counterexamples.append(coefficients)

    witness = (1, 0, 1)
    assert counterexamples
    assert counterexamples[0] == witness
    assert is_nondegenerate(witness)
    assert all(
        vector == ZERO or quadratic(witness, vector) != 0 for vector in VECTORS
    )

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
