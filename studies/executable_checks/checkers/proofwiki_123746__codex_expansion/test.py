"""The displayed identity claims that the pointwise maximum f ∨ g equals (f + g - |f - g|)/2."""

import itertools
import json
from fractions import Fraction

RECORD_ID = "proofwiki_123746__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "On a singleton domain, let f be constantly 0 and g be constantly 1."
REFUTATION_EXPLANATION = "At the unique point, f ∨ g = max(0, 1) = 1, while (f + g - |f - g|)/2 = (0 + 1 - |0 - 1|)/2 = 0. Thus the two sides are unequal."
SEARCH_SPACE = "All 25 ordered pairs of constant functions (f, g) on a singleton domain whose values lie in {-2, -1, 0, 1, 2}, iterated in the fixed value order (0, 1, -1, 2, -2) for each coordinate."

values = (0, 1, -1, 2, -2)
violations = []
for f_value, g_value in itertools.product(values, repeat=2):
    pointwise_maximum = max(f_value, g_value)
    displayed_right_side = Fraction(
        f_value + g_value - abs(f_value - g_value), 2
    )
    if pointwise_maximum != displayed_right_side:
        violations.append((f_value, g_value))

assert len(tuple(itertools.product(values, repeat=2))) == 25
assert violations
assert violations[0] == (0, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
