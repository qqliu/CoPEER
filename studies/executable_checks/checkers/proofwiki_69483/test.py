r"""In the induction step, the transition from line 0052 to line 0055 (justified by 'Corollary: Factors of Binomial Coefficient 2') asserts the identity C(r, j+1) = (j+2)(r-j+2) C(r, j+2), i.e. it replaces the factor \dbinom r {j+1} by \paren{j+2}\paren{r-j+2}\dbinom r {j+2} while leaving the bracketed sum unchanged. This local equality is false."""

import json
from math import comb

pairs = tuple(
    (r, j)
    for r in range(2, 13)
    for j in range(0, r - 1)
)
failures = []
for r, j in pairs:
    left = comb(r, j + 1)
    right = (j + 2) * (r - j + 2) * comb(r, j + 2)
    if left != right:
        failures.append((r, j, left, right))

assert len(pairs) == 66
assert failures
assert failures[0] == (2, 0, 2, 8)

result = {
    "record_id": "proofwiki_69483",
    "outcome": "WITNESS_FOUND",
    "witness_description": "r = 2 and j = 0. Then C(2, 1) = 2, whereas (0+2)(2-0+2)C(2, 2) = 2*4*1 = 8.",
    "refutation_explanation": "The asserted local identity requires 2 = 8 for this admissible pair. Since these exact integer values differ, the identity is false; leaving the bracketed sum unchanged cannot make the asserted replacement an identity.",
    "search_space": "All 66 integer pairs (r, j) with 2 <= r <= 12 and 0 <= j <= r-2, swept in lexicographic order by r and then j."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
