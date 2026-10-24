"""The inequality A < B + 2ε contradicts A > B without any further restriction on ε."""

import itertools
import json

RECORD_ID = "reddit_learnmath_bwzs1p"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "A=1, B=0, ε=1."
REFUTATION_EXPLANATION = (
    "For this witness, A > B because 1 > 0, while A < B + 2ε because "
    "1 < 0 + 2·1 = 2. Thus both inequalities hold simultaneously, so "
    "A < B + 2ε does not contradict A > B without a further restriction on ε."
)
SEARCH_SPACE = (
    "All 27 integer triples (A, B, ε) in {0, 1, 2}^3, swept exhaustively "
    "in itertools.product order."
)

values = range(3)
witnesses = []
for A, B, epsilon in itertools.product(values, repeat=3):
    if A > B and A < B + 2 * epsilon:
        witnesses.append((A, B, epsilon))

assert len(tuple(itertools.product(values, repeat=3))) == 27
assert witnesses
assert witnesses[0] == (1, 0, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
