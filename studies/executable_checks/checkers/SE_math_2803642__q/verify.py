"""From each of $S_1,S_k$ we have to choose exactly $n/2$ elements, thus $n$ elements from both sets. By Pigeonhole principle there exists some $x_i$, such that it is chosen from both $S_1,S_k$ thus forming an edge with both $x_1$ and $x_k$."""

import json

record_id = "SE_math_2803642__q"
labels = tuple("x_" + str(index) for index in range(1, 5))
n = len(labels)
s_1 = frozenset(labels)
s_k = frozenset(labels)
chosen_from_s_1 = frozenset(labels[:2])
chosen_from_s_k = frozenset(labels[2:])

premises_hold = (
    n % 2 == 0
    and s_1 == frozenset(labels)
    and s_k == frozenset(labels)
    and chosen_from_s_1 <= s_1
    and chosen_from_s_k <= s_k
    and len(chosen_from_s_1) * 2 == n
    and len(chosen_from_s_k) * 2 == n
    and len(chosen_from_s_1) + len(chosen_from_s_k) == n
)
common_chosen_label_exists = any(
    label in chosen_from_s_1 and label in chosen_from_s_k
    for label in labels
)
witness_is_counterexample = premises_hold and not common_chosen_label_exists

if witness_is_counterexample:
    verdict = "CONFIRMED"
    notes = "The witness is valid. This is a substantive pigeonhole-principle error, not a typo: exactly n selections among n possible labels need not repeat a label."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The proposed witness does not satisfy the premises or does not refute the asserted common choice."

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
