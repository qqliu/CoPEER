r"""Use the below inequality: For $a>0,b>0,c>0,d>0$,
$(a-b)/(c-d) \leq a/c \iff c(a-b) \leq a(c-d) \iff -bc \leq -ad \iff b/d \geq a/c$"""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "mse_4671334__ans4675111"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The first witness in lexicographic order is (a,b,c,d)=(1,1,1,2). "
    "The four displayed statements have truth values (true,false,false,false)."
)
REFUTATION_EXPLANATION = (
    "For (a,b,c,d)=(1,1,1,2), (a-b)/(c-d)=0/(-1)=0 <= a/c=1, "
    "but c(a-b)=0 is not <= a(c-d)=-1; equivalently, b/d=1/2 is not "
    ">= a/c=1. Thus the first claimed equivalence fails because c-d is "
    "negative, so multiplying by c-d reverses the inequality."
)
SEARCH_SPACE = (
    "All 256 ordered quadruples (a,b,c,d) in {1,2,3,4}^4 were visited in "
    "lexicographic order. The equivalence chain was evaluated exactly for all "
    "192 quadruples with c!=d; the remaining 64 have an undefined first "
    "quotient because c=d."
)

visited = 0
defined = 0
undefined = 0
first_witness = None
first_truth_values = None

for a, b, c, d in product(range(1, 5), repeat=4):
    visited += 1
    if c == d:
        undefined += 1
        continue
    defined += 1
    truth_values = (
        Fraction(a - b, c - d) <= Fraction(a, c),
        c * (a - b) <= a * (c - d),
        -b * c <= -a * d,
        Fraction(b, d) >= Fraction(a, c),
    )
    if first_witness is None and len(set(truth_values)) != 1:
        first_witness = (a, b, c, d)
        first_truth_values = truth_values

assert visited == 256
assert defined == 192
assert undefined == 64
assert first_witness == (1, 1, 1, 2)
assert first_truth_values == (True, False, False, False)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
