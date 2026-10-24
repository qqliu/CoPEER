r"""The proof claims that λx + (1-λ)y equals (1-λ)x + λy for arbitrary x, y, and λ."""

import json

record_id = "reddit_askmath_11qocq8"
notes = (
    "Exact recomputation gives left side 1 and right side 0 for x = 0, y = 1, "
    "λ = 0, so the universal equality is false. The refuted statement is plainly "
    "an algebraic typo, not a substantive mathematical result."
)

x = 0
y = 1
lam = 0
left_side = lam * x + (1 - lam) * y
right_side = (1 - lam) * x + lam * y

assert left_side == 1
assert right_side == 0
assert left_side != right_side

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
