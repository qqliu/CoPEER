r"""Since (as stated in your document), $x_k^2 < 2^m +C$ implies $x_k-\sqrt{C}<1$, that means that $x_k \leqslant \left\lfloor \sqrt{C}\right\rfloor$"""

import json
import math

RECORD_ID = "SE_cs_156858__a156859"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "C=2, m=2, and x_k=2: x_k^2=4<2^m+C=6 and "
    "2-sqrt(2)<1, but floor(sqrt(2))=1, so "
    "x_k<=floor(sqrt(C)) is false."
)
REFUTATION_EXPLANATION = (
    "The inequalities 1<sqrt(2)<2 hold because 1<2<4. Hence "
    "2-sqrt(2)<1, while floor(sqrt(2))=1. Thus this assignment "
    "satisfies both the stated antecedent and its stated intermediate "
    "consequence but violates the claimed bound."
)
SEARCH_SPACE = (
    "All 2,023 triples (C,m,x_k) in {0,...,16} × {0,...,6} × "
    "{-8,...,8}, in fixed lexicographic loop order C, then m, then "
    "x_k; every comparison was evaluated exactly using integers and "
    "math.isqrt."
)


def intermediate_holds(x_k, c):
    """Decide x_k - sqrt(c) < 1 using integer arithmetic."""
    shifted = x_k - 1
    if shifted < 0:
        return True
    return shifted * shifted < c


violations = []
for c in range(17):
    root_floor = math.isqrt(c)
    for m in range(7):
        power = 1 << m
        for x_k in range(-8, 9):
            antecedent = x_k * x_k < power + c
            intermediate = intermediate_holds(x_k, c)
            claimed_bound = x_k <= root_floor
            if antecedent and intermediate and not claimed_bound:
                violations.append((c, m, x_k))

assert violations
assert violations[0] == (2, 2, 2)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
