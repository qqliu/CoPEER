r'''$$\binom{n}{2b+1}\left( \frac{2}{cn\cdot 2^f}\right)^{2b}= \frac{n^{2b+1}}{(2b+1)^{2b+1}} \frac{(2b+1)^{2b+1}}{2^f\cdot cn} = \frac{n}{1}\cdot\frac{1}{4^{f}\cdot n}=\frac{1}{4f}$$ Note that $n^{2b+1}=n^{2b}\cdot n = 2n = n$'''

import json
from fractions import Fraction
from itertools import product
from math import comb

RECORD_ID = "SE_math_4219732__q"
WITNESS_DESCRIPTION = "n=1, b=0, c=1, f=1: binom(1,1)*(2/(1*1*2^1))^0 = 1, while 1/(4*1) = 1/4."
REFUTATION_EXPLANATION = "Under the standard integer binomial-coefficient interpretation, all terms are defined and 1 != 1/4, so the displayed equality chain is false for this tuple."
SEARCH_SPACE = "All 320 tuples with n in {1,...,8}, b in {0,...,3} satisfying 2b+1 <= n, c in {1,...,4}, and f in {1,...,4}, in fixed lexicographic (n,b,c,f) order."

violations = []
checked = 0
for n, b, c, f in product(range(1, 9), range(4), range(1, 5), range(1, 5)):
    if 2 * b + 1 > n:
        continue
    checked += 1
    lhs = Fraction(comb(n, 2 * b + 1), 1) * Fraction(2, c * n * (2 ** f)) ** (2 * b)
    stated_final = Fraction(1, 4 * f)
    if lhs != stated_final:
        violations.append((n, b, c, f, lhs, stated_final))

assert checked == 320
assert violations
first = violations[0]
assert first == (1, 0, 1, 1, Fraction(1, 1), Fraction(1, 4))

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
