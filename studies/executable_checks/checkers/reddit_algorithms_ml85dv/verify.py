r"""The stated CPU schedule can give every enumerated algorithm its prescribed share while reserving one half of CPU time for enumeration."""

import json
from fractions import Fraction

record_id = "reddit_algorithms_ml85dv"
indices = (0, 1)
required = Fraction(1, 2)
for index in indices:
    successor = index + 1
    required += Fraction(1, 2 * successor * successor)

arithmetic_reproduced = required == Fraction(9, 8) and required > Fraction(1, 1)
claim_guarantees_zero_is_natural = False
valid_witness = arithmetic_reproduced and claim_guarantees_zero_is_natural

verdict = "CONFIRMED" if valid_witness else "REFUTED_WITNESS_INVALID"
notes = (
    "Exact arithmetic reproduces 9/8, but the witness assumes without justification "
    "that 0 belongs to ℕ and hence that A_0 is enumerated. If ℕ starts at 1, A_0 is "
    "outside the schedule and this witness does not refute the claim. The scheduling "
    "assertion is substantive, not plainly a typo."
)
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":"), ensure_ascii=False))
