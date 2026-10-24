"""Every prescribed finite system of pairwise distances is realizable in some Euclidean dimension."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_math_1akxj1h",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: exact Gram-matrix arithmetic gives determinant -45/4, so no Euclidean realization exists in any dimension. The refuted universal statement is substantive, not plainly a typo.",
}

# Taking point 0 as the origin, let the displacement vectors to points 1
# and 2 be u and v. Their prescribed squared norms are 1 and 1, while
# the polarization identity forces their inner product from |u-v| = 3.
d01 = 1
d02 = 1
d12 = 3
u_squared = d01 ** 2
v_squared = d02 ** 2
uv = Fraction(u_squared + v_squared - d12 ** 2, 2)
gram_determinant = Fraction(u_squared * v_squared, 1) - uv ** 2

assert (d01, d02, d12) == (1, 1, 3)
assert uv == Fraction(-7, 2)
assert gram_determinant == Fraction(-45, 4)
# Every Gram matrix of real Euclidean vectors is positive semidefinite;
# this negative principal determinant therefore rules out every dimension.
assert gram_determinant < 0
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
