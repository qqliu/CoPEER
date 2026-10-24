"""From nq^2 = p^2, it follows that n divides p."""

import itertools
import json

RECORD_ID = "reddit_learnmath_5bfe9x"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "n=4, p=2, q=1: 4*1^2 = 2^2, but 4 does not divide 2."
REFUTATION_EXPLANATION = (
    "The equation nq^2 = p^2 holds because both sides equal 4. "
    "However, there is no integer k such that 2 = 4*k, so n does not divide p."
)
SEARCH_SPACE = (
    "All 8,000 ordered integer triples (n, p, q) with "
    "1 <= n, p, q <= 20, swept in lexicographic order."
)

first_witness = None
checked = 0

for n, p, q in itertools.product(range(1, 21), repeat=3):
    checked += 1
    equation_holds = n * q * q == p * p
    n_divides_p = p % n == 0
    if equation_holds and not n_divides_p and first_witness is None:
        first_witness = (n, p, q)

assert checked == 8000
assert first_witness == (4, 2, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
