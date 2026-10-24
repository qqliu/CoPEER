"""The sequence f(x_n) = n sin^2(1/n) does not converge and hence is not Cauchy."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_ywskxf"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No finite witness is returned. Refuting nonconvergence requires proving an "
    "infinite tail property, not exhibiting finitely many sequence terms."
)
REFUTATION_EXPLANATION = (
    "Analytically, |sin(1/n)| <= 1/n gives 0 <= n sin^2(1/n) <= 1/n, so the "
    "sequence converges to 0 by squeezing and is therefore Cauchy. This "
    "refutation is a tail proof and cannot be certified by an exhaustive search "
    "of finitely many terms or finitely many epsilon values."
)
SEARCH_SPACE = (
    "Exactly the rational test grid epsilon = 1/q for integers q in {1,...,256} "
    "was swept. For each q, the exact candidate cutoff N=q+1 was checked via "
    "1/N < 1/q. This bounded sweep is illustrative only and is not exhaustive "
    "evidence about convergence."
)

failures = []
for q in range(1, 257):
    cutoff = q + 1
    if not Fraction(1, cutoff) < Fraction(1, q):
        failures.append(q)

assert failures == []

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
