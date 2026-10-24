"""The proof asserts that for an integer a, cont(b n q f) = a * cont(n f), i.e. that pulling an integer scalar a out of the content multiplies the content by a itself. This is false when a (or b) is negative, since the content of an integer polynomial is the GCD of its coefficients and is nonnegative; the correct identity is cont(a g) = |a| cont(g). The proof never splits on the sign of a or b, and the same omission propagates to the final line cont(q f) = (a/b)(1/n) cont(n f) = q cont f."""

import json
from itertools import product
from math import gcd


def content(coefficients):
    result = 0
    for coefficient in coefficients:
        result = gcd(result, coefficient)
    return result


scalars = (-1, 0, 1)
coefficient_values = (-1, 0, 1)
first_witness = None
pairs_checked = 0

for scalar in scalars:
    for length in (1, 2):
        for coefficients in product(coefficient_values, repeat=length):
            pairs_checked += 1
            scaled = tuple(scalar * coefficient for coefficient in coefficients)
            left = content(scaled)
            right = scalar * content(coefficients)
            if first_witness is None and left != right:
                first_witness = (scalar, coefficients, left, right)

assert pairs_checked == 36
assert first_witness == (-1, (-1,), 1, -1)

result = {
    "record_id": "proofwiki_25056",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take the integer scalar a = -1 and the integer polynomial g with coefficient vector (-1,), so g = -1. Then cont(g) = 1 and cont(a g) = cont(1) = 1, whereas a * cont(g) = -1.",
    "refutation_explanation": "The asserted identity cont(a g) = a * cont(g) would require 1 = -1 for this witness. Content is computed as the nonnegative GCD of the coefficients, so a negative scalar contributes its absolute value, not its sign.",
    "search_space": "Exhaustively swept all 36 pairs consisting of a in {-1, 0, 1} and a coefficient vector of length 1 or 2 with every coefficient in {-1, 0, 1}, in fixed scalar/length/lexicographic order. The first violating pair was a = -1 with coefficient vector (-1,).",
}
print(json.dumps(result, separators=(",", ":")))
