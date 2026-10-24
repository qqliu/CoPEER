"""If A ∪ X = B ∪ X, then A = B."""

import json

record_id = "reddit_learnmath_6r8mz6"
a_set = set()
b_set = {0}
x_set = {0}

left_union = {element for element in a_set} | {element for element in x_set}
right_union = {element for element in b_set} | {element for element in x_set}

if left_union == right_union and a_set != b_set:
    verdict = "CONFIRMED"
    notes = "Substantive, not a typo: union with the same set is not cancellative; for A = ∅, B = {0}, and X = {0}, both unions equal {0} although A ≠ B."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Substantive, not a typo: the reported witness does not independently establish failure of the implication."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
