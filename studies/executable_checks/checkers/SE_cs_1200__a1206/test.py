r"""consider the assignment $A[A[0]-1] := A[0]$ under the precondition $A[0] = 2 \wedge A[1] = 3$: you cannot make a simple substitution to obtain the correct postcondition $A[0] = 1 \wedge A[1] = 1$"""

import itertools
import json

record_id = "SE_cs_1200__a1206"
outcome = "WITNESS_FOUND"
witness_description = "The length-2 array A = [2, 3] satisfies A[0] = 2 and A[1] = 3. Evaluating the index and right-hand side in the pre-state makes the assignment A[1] := 2, producing A = [2, 2]."
refutation_explanation = "The resulting array has A[0] = 2 and A[1] = 2, so it does not satisfy A[0] = 1 and A[1] = 1. Thus the claim's express description of that formula as the correct postcondition is contradicted by the concrete execution."
search_space = "All 49 length-2 integer arrays whose two entries are in {-3,-2,-1,0,1,2,3}, in lexicographic product order; exactly one array, [2,3], satisfies the stated precondition, and it was executed."

witnesses = []
precondition_count = 0
for entries in itertools.product(range(-3, 4), repeat=2):
    before = list(entries)
    if before[0] == 2 and before[1] == 3:
        precondition_count += 1
        index = before[0] - 1
        value = before[0]
        after = before[:]
        after[index] = value
        if not (after[0] == 1 and after[1] == 1):
            witnesses.append((before, after, index, value))

assert precondition_count == 1
assert witnesses == [([2, 3], [2, 2], 1, 2)]

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
