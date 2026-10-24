r"""The generalized sum over J converges absolutely to r if and only if the series from n=1 of v_{j_n} converges absolutely to r, although the enumeration begins with j_0."""

import json

record_id = "proofwiki_117692__codex_expansion"
confirmed_notes = "Exact recomputation confirms the counterexample: the generalized sum is absolutely convergent with value 1, while the series beginning at n=1 is absolutely convergent with value 0, not 1. The refuted statement is plainly an indexing typo (n=1 instead of n=0), not a substantive mathematical failure."
invalid_notes = "The reported witness did not pass exact independent verification. The alleged issue would have been a plain indexing typo rather than a substantive mathematical failure."

# The reported family is represented exactly by its finite support:
# v_{j_0}=1, with every other indexed value equal to zero.
support = ((0, 1),)
r = 1

indices = tuple(index for index, value in support if value != 0)
distinct_indices = len(indices) == len(set(indices))
nonnegative_indices = all(index >= 0 for index in indices)

generalized_sum = sum(value for index, value in support)
generalized_absolute_mass = sum(abs(value) for index, value in support)
series_from_one_sum = sum(value for index, value in support if index >= 1)
series_from_one_absolute_mass = sum(abs(value) for index, value in support if index >= 1)

left_holds = (
    distinct_indices
    and nonnegative_indices
    and generalized_absolute_mass == 1
    and generalized_sum == r
)
right_holds = (
    series_from_one_absolute_mass == 0
    and series_from_one_sum == r
)
witness_refutes_equivalence = (
    left_holds
    and not right_holds
    and series_from_one_sum == 0
    and r != 0
)

if witness_refutes_equivalence:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = invalid_notes

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
