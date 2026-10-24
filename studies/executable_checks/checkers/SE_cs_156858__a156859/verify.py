r"""Since (as stated in your document), $x_k^2 < 2^m +C$ implies $x_k-\sqrt{C}<1$, that means that $x_k \leqslant \left\lfloor \sqrt{C}\right\rfloor$"""

import json

record_id = "SE_cs_156858__a156859"
confirmed_notes = "Exact integer recomputation validates C=2, m=2, x_k=2: 4<6; 2-sqrt(2)<1 because 1^2<2; floor(sqrt(2))=1; and 2<=1 is false. The refuted statement is substantive, not plainly a typo."
invalid_notes = "The exact recomputation did not validate the reported witness. The alleged refutation would therefore be invalid; the statement appears substantive rather than plainly a typo."

c = 2
m = 2
x_k = 2

antecedent = x_k * x_k < (1 << m) + c

# For c >= 0, x_k - sqrt(c) < 1 is automatic when x_k - 1 < 0;
# otherwise it is exactly equivalent to (x_k - 1)^2 < c.
offset = x_k - 1
intermediate = c >= 0 and (offset < 0 or offset * offset < c)

root_floor = 0
while (root_floor + 1) * (root_floor + 1) <= c:
    root_floor += 1
floor_characterized = root_floor * root_floor <= c < (root_floor + 1) * (root_floor + 1)
claimed_bound_fails = x_k > root_floor

established = antecedent and intermediate and floor_characterized and claimed_bound_fails
verdict = "CONFIRMED" if established else "REFUTED_WITNESS_INVALID"
notes = confirmed_notes if established else invalid_notes

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
