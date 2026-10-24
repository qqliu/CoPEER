r"""If u divides mn and gcd(u,m)=1, then m=±1."""

import json

REPORT = {
    "record_id": "reddit_learnmath_a2vtxz",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not plainly a typo: u=2 divides m*n=6 and gcd(2,3)=1, while m=3 is neither 1 nor -1.",
}


def exact_gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b != 0:
        a, b = b, a % b
    return a


u = 2
m = 3
n = 2
product = m * n

assert u != 0
assert product == 6
assert product % u == 0
assert exact_gcd(u, m) == 1
assert m != 1
assert m != -1
assert m not in (1, -1)

print(json.dumps(REPORT, ensure_ascii=False))
