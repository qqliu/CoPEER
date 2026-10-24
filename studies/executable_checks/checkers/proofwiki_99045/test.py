r"""In Case 3, sub-case i != 1 and j != 2 with i = 2 and k = 1, the proof selects l from N_n \ {1,2,3,k} and asserts that sigma = (1, 2, j, l, 3) is an even permutation with sigma(1)=i, sigma(2)=j, sigma(3)=k. The exclusion set is wrong: since k = 1 in this sub-case, the constraint reduces to l not in {1,2,3}, which does not exclude l = j, and the displayed 5-cycle requires l != j to even be a well-defined cycle."""

import json

RECORD_ID = "proofwiki_99045"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take n=5, i=2, k=1, j=4, and l=4. Then l belongs to "
    "N_5 \\ {1,2,3,k}={4,5}, but the displayed tuple is (1,2,4,4,3)."
)
REFUTATION_EXPLANATION = (
    "The value 4 occurs twice in (1,2,4,4,3), so it is not a well-defined "
    "5-cycle. Thus the stated exclusion permits a choice of l for which the "
    "displayed permutation is undefined; excluding l=j is necessary."
)
SEARCH_SPACE = (
    "All 8 assignments with n=5, i=2, k=1, j in {1,3,4,5}, and l in "
    "N_5 \\ {1,2,3,k}={4,5}, swept in lexicographic (j,l) order."
)

n = 5
i = 2
k = 1
allowed_j = tuple(j for j in range(1, n + 1) if j != 2)
allowed_l = tuple(l for l in range(1, n + 1) if l not in {1, 2, 3, k})
witnesses = []
assignments_checked = 0

for j in allowed_j:
    for l in allowed_l:
        assignments_checked += 1
        displayed_cycle = (1, 2, j, l, 3)
        if l == j and len(set(displayed_cycle)) != 5:
            witnesses.append((n, i, k, j, l, displayed_cycle))

expected = (5, 2, 1, 4, 4, (1, 2, 4, 4, 3))
if assignments_checked != 8 or not witnesses or witnesses[0] != expected:
    raise RuntimeError("deterministic exhaustive search produced an unexpected result")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
