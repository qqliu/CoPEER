r"""Inside the AimForCont argument the proof asserts the inclusion step \bigcup_{j = 1, j \ne i}^{m - 1} \paren{D_j \cup D_m} \subseteq \bigcup_{j = 1, j \ne i}^{m - 1} D_j, i.e. that the copy of D_m may simply be dropped from the union. This inclusion is false in general (the correct direction is the reverse), so the derivation of d_i \in E_i \subseteq \bigcup_{j \ne i}^{m-1} D_j is not justified by the stated steps."""

import json

record_id = "proofwiki_133598"
verdict = "CONFIRMED"
notes = "Independent exact recomputation confirms the witness: with m=3, i=1, D_2 empty, and D_3={0}, the left union is {0} while the right union is empty, so the asserted inclusion fails. The refuted statement is substantive, not plainly a typo, because the quoted derivation relies on that invalid inclusion."

m = 3
i = 1
universe_mask = 1
sets = {1: 0, 2: 0, 3: 1}
indices = tuple(j for j in range(1, m) if j != i)

left_mask = 0
right_mask = 0
for j in indices:
    left_mask |= sets[j] | sets[m]
    right_mask |= sets[j]

assert indices == (2,)
assert all((mask | universe_mask) == universe_mask for mask in sets.values())
assert left_mask == universe_mask
assert right_mask == 0
assert left_mask & (universe_mask ^ right_mask)

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
