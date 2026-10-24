r"""**Lemma**: let $m,n \in \mathbb{N}$. Then, the set $\{2,...,m\}$ contains (at least) as many multiples of $n$ as $\{m+2, ..., 2m\}$."""

import json

m = 2
n = 4
left = tuple(value for value in range(2, m + 1))
right = tuple(value for value in range(m + 2, 2 * m + 1))
left_count = len(tuple(value for value in left if value % n == 0))
right_count = len(tuple(value for value in right if value % n == 0))

if m >= 1 and n >= 1 and left == (2,) and right == (4,) and left_count == 0 and right_count == 1 and left_count < right_count:
    verdict = "CONFIRMED"
    notes = "Exact recomputation gives left set {2} with 0 multiples of 4 and right set {4} with 1 multiple of 4. Thus the stated universal claim fails at m=2, n=4. The refuted statement is substantive as written, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact recomputation did not establish the reported counterexample. The statement would therefore remain unrefuted by this witness and is not plainly a typo."

print(json.dumps({"record_id": "SE_math_4537650__q", "verdict": verdict, "notes": notes}, separators=(",", ":")))
