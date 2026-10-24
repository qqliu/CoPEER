r'''For every set X, taking A = X ∪ P(X) satisfies the theorem's hypothesis A ⊆ P(A).'''

import json
from itertools import combinations


def exact_power_set(value):
    elements = tuple(value)
    subsets = []
    for size in range(len(elements) + 1):
        for selection in combinations(elements, size):
            subsets.append(frozenset(selection))
    return frozenset(subsets)


empty = frozenset()
single_empty = frozenset([empty])
double_empty = frozenset([single_empty])
witness_x = frozenset([double_empty])

computed_power_x = exact_power_set(witness_x)
computed_a = witness_x.union(computed_power_x)
reported_power_x = frozenset([empty, witness_x])
reported_a = frozenset([empty, double_empty, witness_x])
computed_power_a = exact_power_set(computed_a)

checks = (
    computed_power_x == reported_power_x,
    computed_a == reported_a,
    double_empty in computed_a,
    single_empty in double_empty,
    single_empty not in computed_a,
    not double_empty.issubset(computed_a),
    double_empty not in computed_power_a,
    not computed_a.issubset(computed_power_a),
)
assert all(checks)

result = {
    "record_id": "reddit_learnmath_538hc0",
    "verdict": "CONFIRMED",
    "notes": "Exact hereditary-finite-set recomputation validates the witness: for X={{{∅}}}, A contains {{∅}} but not its element {∅}, so A is not a subset of P(A). The refuted universal statement is substantive, not plainly a typo."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
