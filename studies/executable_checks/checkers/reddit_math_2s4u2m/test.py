"""A 565248-bit encoding of Hamlet has approximately 390,000 base-10 digits."""

import json

RECORD_ID = "reddit_math_2s4u2m"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample is reported: the sweep only evaluates one conventional "
    "canonical-integer interpretation, which the supplied data do not require."
)
REFUTATION_EXPLANATION = (
    "Under the conventional unsigned-integer, no-leading-zero interpretation, "
    "exact arithmetic gives at most 170,157 decimal digits, so exactly 390,000 "
    "is impossible. But \"approximately\" has no tolerance, and neither the "
    "mapping from Hamlet's encoding to a base-10 string nor the treatment of "
    "leading zeros is specified; therefore this bounded sweep cannot decide "
    "the stated claim without inventing definitions."
)
SEARCH_SPACE = (
    "All 390,000 integer candidate canonical decimal lengths d from 1 through "
    "390,000, each classified against the exact maximum value 2^565248 - 1; "
    "the maximum feasible d is 170,157."
)

bit_count = 565248
largest_unsigned_value = (1 << bit_count) - 1

lower = 1
upper = 390000
while lower < upper:
    midpoint = (lower + upper + 1) // 2
    if 10 ** (midpoint - 1) <= largest_unsigned_value:
        lower = midpoint
    else:
        upper = midpoint - 1
maximum_feasible_digits = lower

feasible_count = 0
named_length_is_feasible = False
for candidate_digits in range(1, 390001):
    is_feasible = candidate_digits <= maximum_feasible_digits
    if is_feasible:
        feasible_count += 1
    if candidate_digits == 390000:
        named_length_is_feasible = is_feasible

assert maximum_feasible_digits == 170157
assert feasible_count == 170157
assert not named_length_is_feasible

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
