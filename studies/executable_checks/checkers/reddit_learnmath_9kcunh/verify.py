r"""The proof claims that 4/(sqrt(n)+2) < 1/n for the relevant natural numbers n."""

import json
from fractions import Fraction

n = 1
root = 1
left = Fraction(4, root + 2)
right = Fraction(1, n)

assert n > 0
assert root * root == n
assert left == Fraction(4, 3)
assert right == Fraction(1, 1)
assert left > right

result = {
    "record_id": "reddit_learnmath_9kcunh",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic confirms the reported witness: at n = 1, sqrt(n) = 1, so the left side is 4/3, which is greater than 1/n = 1. Thus the strict inequality fails. The refuted statement is a substantive mathematical error, not a plainly identifiable typo."
}
print(json.dumps(result, separators=(",", ":")))
