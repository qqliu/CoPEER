"""The constructed inequalities M - 1/n < f(x_n) ≤ M imply |M - x_n| < 1/n and hence x_n → M."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_47268__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified witness: the quote supplies |M - x_n| < 1/n directly but "
    "gives no definition of f or relation between f(x_n) and x_n."
)
REFUTATION_EXPLANATION = (
    "The bounded sweep finds formal numeric assignments where M - 1/n < y <= M "
    "while |M - x| >= 1/n if y is treated independently, but y cannot be "
    "certified as f(x_n) for the unspecified constructed objects without "
    "inventing missing definitions. Thus the alleged implication is unsupported "
    "by the permitted data, but a contextual counterexample is not decidable."
)
SEARCH_SPACE = (
    "Exhaustively swept 750 tuples (n, M, x, y) with n in {1, ..., 6} and "
    "M, x, y in {-2, -1, 0, 1, 2}, using y only as a placeholder for f(x_n), "
    "in lexicographic order; this is illustrative, not exhaustive over "
    "unspecified functions or sequences."
)

values = range(-2, 3)
formal_violations = 0
tuples_checked = 0

for n in range(1, 7):
    reciprocal = Fraction(1, n)
    for m_integer in values:
        m = Fraction(m_integer, 1)
        for x_integer in values:
            x = Fraction(x_integer, 1)
            for y_integer in values:
                y = Fraction(y_integer, 1)
                tuples_checked += 1
                premise = m - reciprocal < y and y <= m
                conclusion_fails = abs(m - x) >= reciprocal
                if premise and conclusion_fails:
                    formal_violations += 1

assert tuples_checked == 750
assert formal_violations > 0

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result))
