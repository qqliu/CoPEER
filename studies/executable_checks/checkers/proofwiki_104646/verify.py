r"""The proof asserts that the configuration it just described (elements x1,y1,x2,y2 with z1 = x1∘y1, z2 = x2∘y2, z1 ≠ z2, ¬(z1=x1 ∧ z2=x2), ¬(z1=y1 ∧ z2=y2), for an operation ∘ that is none of the right/left/constant operations) can occur only when |S| > 3. This is false: an explicit 3-element set with an explicit operation table realizes all of the stated conditions, so the proof's cardinality claim (which would also wrongly exclude the |S| = 3 case allowed by the hypothesis "at least 3 elements") is refuted by a finite witness."""

import json

record_id = "proofwiki_104646"
confirmed_notes = "Exact recomputation validates the 3-element total operation and witness: z1=0, z2=1; both forbidden conjunctions are false; the table is neither projection nor constant. Thus the >3 assertion is genuinely false. This is a substantive false statement as written, although replacing “more than 3” with “at least 3” could have been an intended boundary typo; the supplied evidence does not make it plainly a typo."
invalid_notes = "The reported concrete witness does not satisfy every stated condition, so it does not refute the claim. The substantive-versus-typo classification cannot be established from an invalid witness."

carrier = frozenset((0, 1, 2))
operation = {
    (0, 0): 0, (0, 1): 0, (0, 2): 0,
    (1, 0): 0, (1, 1): 0, (1, 2): 0,
    (2, 0): 0, (2, 1): 0, (2, 2): 1,
}

pairs = tuple((a, b) for a in carrier for b in carrier)
total_domain = frozenset(operation) == frozenset(pairs)
closed = total_domain and all(operation[pair] in carrier for pair in pairs)

x1, y1, x2, y2 = 0, 0, 2, 2
arguments_in_carrier = all(value in carrier for value in (x1, y1, x2, y2))
z1 = operation[(x1, y1)]
z2 = operation[(x2, y2)]

left_projection = all(operation[(a, b)] == a for a, b in pairs)
right_projection = all(operation[(a, b)] == b for a, b in pairs)
output_values = frozenset(operation[pair] for pair in pairs)
constant_operation = len(output_values) == 1

configuration_holds = (
    len(carrier) == 3
    and closed
    and arguments_in_carrier
    and z1 != z2
    and not (z1 == x1 and z2 == x2)
    and not (z1 == y1 and z2 == y2)
    and not left_projection
    and not right_projection
    and not constant_operation
)

if configuration_holds:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = invalid_notes

print(json.dumps(
    {"record_id": record_id, "verdict": verdict, "notes": notes},
    ensure_ascii=False,
    separators=(",", ":"),
))
