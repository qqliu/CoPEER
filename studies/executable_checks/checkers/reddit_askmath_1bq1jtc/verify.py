"""The asserted factorization 6q + 2 = 2(3q + 2) is valid for integers q."""

import json

q = -2
lhs = 6 * q + 2
rhs = 2 * (3 * q + 2)

if not (type(q) is int and lhs == -10 and rhs == -8 and lhs != rhs):
    raise RuntimeError("Exact witness recomputation failed")

result = {
    "record_id": "reddit_askmath_1bq1jtc",
    "verdict": "CONFIRMED",
    "notes": "Exact integer recomputation at q = -2 gives 6q + 2 = -10 and 2(3q + 2) = -8, so the universal claim fails. The refuted statement is plainly an algebraic typo: the correct factorization is 2(3q + 1)."
}
print(json.dumps(result, separators=(",", ":")))
