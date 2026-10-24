"""The proof asserts that the configuration it just described (elements x1,y1,x2,y2 with z1 = x1∘y1, z2 = x2∘y2, z1 ≠ z2, ¬(z1=x1 ∧ z2=x2), ¬(z1=y1 ∧ z2=y2), for an operation ∘ that is none of the right/left/constant operations) can occur only when |S| > 3. This is false: an explicit 3-element set with an explicit operation table realizes all of the stated conditions, so the proof's cardinality claim (which would also wrongly exclude the |S| = 3 case allowed by the hypothesis "at least 3 elements") is refuted by a finite witness."""

import itertools
import json

RECORD_ID = "proofwiki_104646"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let S={0,1,2} and define ∘ by the rows x=0:[0,0,0], "
    "x=1:[0,0,0], x=2:[0,0,1], with columns y=0,1,2. "
    "Choose (x1,y1,x2,y2)=(0,0,2,2); then (z1,z2)=(0,1)."
)
REFUTATION_EXPLANATION = (
    "Here z1≠z2. Also ¬(z1=x1 ∧ z2=x2) and "
    "¬(z1=y1 ∧ z2=y2), because z2=1 differs from x2=y2=2. "
    "The operation is nonconstant, is not the left projection since "
    "1∘0=0≠1, and is not the right projection since 0∘1=0≠1. "
    "Thus every stated condition occurs on exactly three elements, "
    "contradicting the assertion that more than three are necessary."
)
SEARCH_SPACE = (
    "All 3^9=19683 operation tables S×S→S on S={0,1,2}, and for "
    "every table all 3^4=81 ordered quadruples (x1,y1,x2,y2), "
    "totaling 1594323 table/quadruple combinations, in lexicographic "
    "product order."
)

S = (0, 1, 2)
first_witness = None
checked = 0

for table in itertools.product(S, repeat=9):
    is_left = all(table[3 * x + y] == x for x in S for y in S)
    is_right = all(table[3 * x + y] == y for x in S for y in S)
    is_constant = all(value == table[0] for value in table)

    for x1, y1, x2, y2 in itertools.product(S, repeat=4):
        checked += 1
        if is_left or is_right or is_constant:
            continue
        z1 = table[3 * x1 + y1]
        z2 = table[3 * x2 + y2]
        valid = (
            z1 != z2
            and not (z1 == x1 and z2 == x2)
            and not (z1 == y1 and z2 == y2)
        )
        if valid and first_witness is None:
            first_witness = (table, (x1, y1, x2, y2), (z1, z2))

assert checked == 1594323
assert first_witness == (
    (0, 0, 0, 0, 0, 0, 0, 0, 1),
    (0, 0, 2, 2),
    (0, 1),
)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
