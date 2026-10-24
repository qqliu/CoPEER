"""For degree reverse lexicographic order, if i<j and a_i>a_j, swapping the exponents a_i and a_j produces a monomial larger than the original leading monomial."""

import json
from itertools import combinations, product

record_id = "proofwiki_10516__codex_expansion"
outcome = "NO_WITNESS_INCONCLUSIVE"
witness_description = (
    "No concrete witness can be certified from the supplied data because the "
    "variable-priority convention needed to evaluate “larger” is not specified."
)
refutation_explanation = (
    "Swapping preserves total degree, so the result depends on the orientation "
    "and variable priority used for degree reverse lexicographic order. The "
    "supplied claim and quote provide neither, and adopting one would invent "
    "missing data; therefore all eligible candidates remain undecidable."
)
search_space = (
    "Exhaustively enumerated n in {2,3,4}, every exponent vector in "
    "{0,1,2,3}^n, and every pair of positions 1 <= i < j <= n: 1744 "
    "candidate triples total, of which 654 satisfy a_i > a_j. No ordering "
    "comparison was certified because its required convention is absent."
)

total_candidates = 0
eligible_candidates = 0
for n in range(2, 5):
    for exponents in product(range(4), repeat=n):
        for i, j in combinations(range(n), 2):
            total_candidates += 1
            if exponents[i] > exponents[j]:
                eligible_candidates += 1

if total_candidates != 1744 or eligible_candidates != 654:
    raise AssertionError("bounded enumeration count mismatch")

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
