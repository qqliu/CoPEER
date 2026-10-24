r"""In Case 3, sub-case i != 1 and j != 2 with i = 2 and k = 1, the proof selects l from N_n \ {1,2,3,k} and asserts that sigma = (1, 2, j, l, 3) is an even permutation with sigma(1)=i, sigma(2)=j, sigma(3)=k. The exclusion set is wrong: since k = 1 in this sub-case, the constraint reduces to l not in {1,2,3}, which does not exclude l = j, and the displayed 5-cycle requires l != j to even be a well-defined cycle."""

import json

record_id = "proofwiki_99045"
confirmed_notes = "Substantive, though locally repairable: with n=5, i=2, k=1, j=4, the stated exclusion permits l=4, producing (1,2,4,4,3), which has a repeated entry and therefore is not a well-defined 5-cycle. This is a logical omission, not plainly a typographical error."
invalid_notes = "The concrete assignment did not independently satisfy every stated constraint or did not make the displayed cycle ill-defined."

n = 5
i = 2
j = 4
k = 1
l = 4

letters = set(range(1, n + 1))
excluded = {1, 2, 3, k}
permitted_l = letters.difference(excluded)
cycle_entries = (1, 2, j, l, 3)

case_holds = n >= 5 and i != 1 and j != 2 and i == 2 and k == 1
selection_holds = l in permitted_l
exclusion_reduces_as_claimed = excluded == {1, 2, 3}
cycle_uses_letters = all(entry in letters for entry in cycle_entries)
well_defined_five_cycle = cycle_uses_letters and len(cycle_entries) == 5 and len(set(cycle_entries)) == 5
repetition_is_j_and_l = j == l and cycle_entries.count(j) == 2

confirmed = (
    case_holds
    and selection_holds
    and exclusion_reduces_as_claimed
    and repetition_is_j_and_l
    and not well_defined_five_cycle
)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if confirmed else invalid_notes,
}
print(json.dumps(result, separators=(",", ":")))
