"""The inequalities b − ε < q < b with q rational imply q ∈ T = ℚ ∩ [a,b]."""

import json


def less(left, right):
    return left[0] * right[1] < right[0] * left[1]


def subtract(left, right):
    return (
        left[0] * right[1] - right[0] * left[1],
        left[1] * right[1],
    )


a = (0, 1)
b = (1, 1)
epsilon = (2, 1)
q = (-1, 2)

valid_representations = all(
    isinstance(number, int) and isinstance(denominator, int) and denominator > 0
    for number, denominator in (a, b, epsilon, q)
)
b_minus_epsilon = subtract(b, epsilon)
antecedent = (
    valid_representations
    and less(b_minus_epsilon, q)
    and less(q, b)
)
q_in_closed_interval = not less(q, a) and not less(b, q)
claim_fails = antecedent and not q_in_closed_interval

if claim_fails:
    verdict = "CONFIRMED"
    notes = (
        "The witness is valid under exact arithmetic: −1 < −1/2 < 1, while "
        "−1/2 is rational but not in [0,1]. The refuted statement is "
        "substantive, not plainly a typo; it lacks a premise ensuring "
        "b − ε ≥ a (or otherwise q ≥ a)."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = (
        "The proposed values do not establish the claimed counterexample. "
        "The statement would still be substantive rather than plainly a typo."
    )

print(json.dumps({
    "record_id": "reddit_learnmath_17ywzl4",
    "verdict": verdict,
    "notes": notes,
}, ensure_ascii=False, separators=(",", ":")))
