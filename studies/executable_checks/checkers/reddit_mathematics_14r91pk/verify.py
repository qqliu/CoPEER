r"""For every natural number x, x+2 < -x²+x³."""

import json

REPORT = {
    "record_id": "reddit_mathematics_14r91pk",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation gives x+2 = 3 and -x²+x³ = 0 at the natural number x = 1, so 3 < 0 is false. The refuted statement is substantive as written, not plainly a typo; it would require a restriction such as x >= 3."
}

x = 1
assert isinstance(x, int) and not isinstance(x, bool)
assert x >= 1

left = x + 2
x_squared = x * x
x_cubed = x_squared * x
right = -x_squared + x_cubed

assert left == 3
assert right == 0
assert not (left < right)
assert set(REPORT) == {"record_id", "verdict", "notes"}
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
