"""For every set X, taking A = X ∪ P(X) satisfies the theorem's hypothesis A ⊆ P(A)."""

import json


def power_set(value):
    items = tuple(value)
    return frozenset(
        frozenset(items[index] for index in range(len(items)) if mask & (1 << index))
        for mask in range(1 << len(items))
    )


empty = frozenset()
single_empty = frozenset((empty,))
double_empty = frozenset((single_empty,))
pair = frozenset((empty, single_empty))
ordered_v3 = (empty, single_empty, double_empty, pair)

violations = []
for mask in range(1 << len(ordered_v3)):
    candidate_x = frozenset(
        ordered_v3[index]
        for index in range(len(ordered_v3))
        if mask & (1 << index)
    )
    candidate_a = candidate_x | power_set(candidate_x)
    if not candidate_a <= power_set(candidate_a):
        violations.append((mask, candidate_x, candidate_a))

expected_x = frozenset((double_empty,))
expected_a = expected_x | power_set(expected_x)
assert violations
assert violations[0] == (4, expected_x, expected_a)
assert double_empty in expected_a
assert single_empty in double_empty
assert single_empty not in expected_a

result = {
    "record_id": "reddit_learnmath_538hc0",
    "outcome": "WITNESS_FOUND",
    "witness_description": "X = {{{∅}}}; then P(X) = {∅, {{{∅}}}} and A = {∅, {{∅}}, {{{∅}}}}.",
    "refutation_explanation": "For x = {{∅}} ∈ A, its element {∅} is not in A; hence x ⊄ A, so x ∉ P(A) and therefore A ⊄ P(A).",
    "search_space": "All 16 subsets X of V_3, where V_0 = ∅ and V_(n+1) = P(V_n), enumerated by masks 0 through 15 in the fixed element order (∅, {∅}, {{∅}}, {∅, {∅}}). Every candidate was tested."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
