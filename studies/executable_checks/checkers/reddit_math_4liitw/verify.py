r"""(P⇒Q) ∧ (Q⇒R) is equivalent to P⇒R."""

import json

REPORT = {
    "record_id": "reddit_math_4liitw",
    "verdict": "CONFIRMED",
    "notes": "Exact Boolean recomputation at P=False, Q=True, R=False gives left=False and right=True; the refuted equivalence is substantive, not plainly a typo.",
}


def material_implication(antecedent, consequent):
    assert antecedent in (0, 1)
    assert consequent in (0, 1)
    return 1 - antecedent * (1 - consequent)


p, q, r = 0, 1, 0
p_implies_q = material_implication(p, q)
q_implies_r = material_implication(q, r)
left = p_implies_q * q_implies_r
right = material_implication(p, r)

assert (p, q, r) == (0, 1, 0)
assert p_implies_q == 1
assert q_implies_r == 0
assert left == 0
assert right == 1
assert left != right

print(json.dumps(REPORT, separators=(",", ":")))
