"""If X is the largest integer for which the coefficients of a normalized newform f and its quadratic twist f′ agree for every n≤X, then χ(n) is nonnegative for every n≤X."""

import json
from itertools import product

RECORD_ID = "arxiv_1102.4582v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No certified witness: 10,098 raw tables have the formal pattern of first disagreement at X+1 and a negative chi value at some n<=X, but the supplied data do not determine whether any table comes from a normalized newform and its quadratic twist."
REFUTATION_EXPLANATION = "The quote merely asserts that chi(n) is nonnegative by definition; it supplies neither that definition nor a coefficient-twist relation or an admissibility test for normalized newforms and quadratic twists. Consequently the bounded raw-table sweep cannot certify a mathematical counterexample."
SEARCH_SPACE = "Exhaustively swept 551,853 raw tables: X in {1,2,3}; for each n in {1,...,X+1}, independently a_n, a'_n, and chi(n) in {-1,0,1}. Exactly 10,098 tables had a_n=a'_n for n<=X, a_(X+1)!=a'_(X+1), and chi(n)<0 for some n<=X; realizability as the named mathematical objects is undecidable from the supplied data."

values = (-1, 0, 1)
examined = 0
formal_candidates = 0

for x in range(1, 4):
    width = x + 1
    for raw in product(values, repeat=3 * width):
        examined += 1
        a = raw[:width]
        a_twist = raw[width:2 * width]
        chi = raw[2 * width:]
        agrees_through_x = all(a[i] == a_twist[i] for i in range(x))
        first_boundary_disagrees = a[x] != a_twist[x]
        has_negative_chi = any(chi[i] < 0 for i in range(x))
        if agrees_through_x and first_boundary_disagrees and has_negative_chi:
            formal_candidates += 1

assert examined == 551853
assert formal_candidates == 10098

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
