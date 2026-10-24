"""If bi > 0, the maximum of yTx subject to aT
i x ≤bi is yT ai
bi
(achieved at x = ai
bi ), so we
must have yT ai
bi
≤1, i.e., yTai ≤bi."""

import json
from fractions import Fraction

record_id = "Algorithms_43__sol5"
notes = "Exact scalar arithmetic confirms the witness: with ai=1, bi=2, and y=1, feasibility is x≤2, so the maximum is 2 at x=2, whereas the claimed value is 1/2. The refuted statement is substantive as written, not plainly a typo."

ai = Fraction(1, 1)
bi = Fraction(2, 1)
y = Fraction(1, 1)
x = Fraction(2, 1)

claimed_maximum = Fraction(y.numerator * ai.numerator, bi.numerator)
actual_maximum = Fraction(bi.numerator, ai.numerator)
objective = y * x
feasible = ai * x <= bi
established = (
    bi > 0
    and ai > 0
    and y > 0
    and feasible
    and x == actual_maximum
    and objective == y * actual_maximum
    and objective > claimed_maximum
)

verdict = "CONFIRMED" if established else "REFUTED_WITNESS_INVALID"
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
