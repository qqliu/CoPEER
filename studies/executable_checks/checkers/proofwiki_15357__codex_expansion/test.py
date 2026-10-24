"""For an arbitrary G-module V over an algebraically closed field, if a G-module automorphism f has eigenvalue λ, then Schur's Lemma implies f = λI_V, without requiring V to be irreducible."""

import json
from itertools import product

VALUES = (-2, -1, 1, 2)
witnesses = []
checked = 0

for a, b, lam in product(VALUES, repeat=3):
    checked += 1
    determinant = a * b
    is_automorphism = determinant != 0
    has_eigenvalue = lam == a or lam == b
    is_scalar_lam = a == lam and b == lam
    if is_automorphism and has_eigenvalue and not is_scalar_lam:
        witnesses.append((a, b, lam))

assert checked == 64
assert witnesses
assert witnesses[0] == (-2, -1, -2)

result = {
    "record_id": "proofwiki_15357__codex_expansion",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Over the algebraically closed field C, let G be the trivial group, let V=C^2 with the trivial action, and let f=diag(-2,-1). Then f is a G-module automorphism and λ=-2 is an eigenvalue, but f≠-2I_V.",
    "refutation_explanation": "The determinant of f is 2, so f is invertible; under the trivial G-action, f and its inverse are G-module homomorphisms. Moreover, f(1,0)=-2(1,0), while f(0,1)=-(0,1)≠-2(0,1). Thus λ=-2 is an eigenvalue but f is not λI_V, directly violating the claimed conclusion. The module is reducible, which is precisely the omitted hypothesis.",
    "search_space": "All 64 triples (a,b,λ) in {-2,-1,1,2}^3 were checked in fixed lexicographic product order, with diag(a,b) interpreted as a linear map on the trivial-group module C^2. Every such matrix is invertible, and the test checks exactly whether λ is one of its diagonal eigenvalues and whether the matrix differs from λI."
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
