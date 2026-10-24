"""Algorithm 1 computes C(1,n,D) by implementing the stated dynamic-programming recurrence."""

import itertools
import json


VALUES = (-1, 0, 1)
examined = 0
local_discrepancy_found = False

for i in (0, 1):
    for offset in (2, 3):
        j = i + offset
        for k in range(i + 1, j + 1):
            for w in (1, 2):
                for old_min in VALUES:
                    for guard_left, guard_right, update_left, update_right in itertools.product(VALUES, repeat=4):
                        examined += 1
                        guard_holds = guard_left + guard_right <= old_min
                        assigned_min = update_left + update_right
                        if guard_holds and assigned_min > old_min:
                            local_discrepancy_found = True

assert examined == 4860
assert local_discrepancy_found

result = {
    "record_id": "arxiv_2501.11129v3__source_enriched_codex",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No claim-level witness is certified. The sweep finds local valuations where the quoted guard is true and the quoted assignment raises min, but the quote supplies no constraints showing that such a valuation can occur in Algorithm 1.",
    "refutation_explanation": "The source quote omits the stated recurrence, definitions and base cases for C, the domains of n and D, the initialization of min, and the remainder of Algorithm 1. Therefore arbitrary exact valuations of the four displayed C entries cannot be promoted to an input on which the algorithm returns an incorrect C(1,n,D).",
    "search_space": "Exhaustively swept 4,860 local valuations: i in {0,1}; j in {i+2,i+3}; k in {i+1,...,j}; w in {1,2}; old min in {-1,0,1}; and independent values in {-1,0,1} for C(i,k,w), C(k+1,j,w-1), C(i,k-1,w), and C(k,j,w-1). This is an illustrative finite local model, not an exhaustive space of Algorithm 1 inputs."
}

print(json.dumps(result, separators=(",", ":")))
