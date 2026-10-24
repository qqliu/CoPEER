r"""For an arbitrary G-module V over an algebraically closed field, if a G-module automorphism f has eigenvalue λ, then Schur's Lemma implies f = λI_V, without requiring V to be irreducible."""

import json
from fractions import Fraction

record_id = "proofwiki_15357__codex_expansion"
verdict = "CONFIRMED"
notes = "Exact recomputation confirms the witness: on the trivial-group module C^2, diag(-2,-1) is an invertible G-equivariant map, -2 is an eigenvalue, and the map is not -2 times the identity. The refuted statement is substantive, not a typo: it omits the irreducibility hypothesis needed for this application of Schur's Lemma."

zero = Fraction(0, 1)
one = Fraction(1, 1)
lam = Fraction(-2, 1)
f_matrix = (
    (Fraction(-2, 1), zero),
    (zero, Fraction(-1, 1)),
)
f_inverse = (
    (Fraction(-1, 2), zero),
    (zero, Fraction(-1, 1)),
)
identity = ((one, zero), (zero, one))


def mat_vec(matrix, vector):
    return tuple(
        sum((entry * coordinate for entry, coordinate in zip(row, vector)), zero)
        for row in matrix
    )


def mat_mul(left, right):
    return tuple(
        tuple(
            sum((left[i][k] * right[k][j] for k in range(2)), zero)
            for j in range(2)
        )
        for i in range(2)
    )


def trivial_action(vector):
    return vector


eigenvector = (one, zero)
second_basis_vector = (zero, one)

assert mat_mul(f_matrix, f_inverse) == identity
assert mat_mul(f_inverse, f_matrix) == identity
assert mat_vec(f_matrix, trivial_action(eigenvector)) == trivial_action(mat_vec(f_matrix, eigenvector))
assert mat_vec(f_matrix, trivial_action(second_basis_vector)) == trivial_action(mat_vec(f_matrix, second_basis_vector))
assert mat_vec(f_matrix, eigenvector) == tuple(lam * coordinate for coordinate in eigenvector)
assert mat_vec(f_matrix, second_basis_vector) != tuple(lam * coordinate for coordinate in second_basis_vector)

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
