r"""$$g(n) = \displaystyle n^{\log_b a} \log_b^k n \; \sum_{j=0}^{\log_b{n-1}}  \left(\frac{a}{b^{\log_b a}}\right)^j = n^{\log_b a} \log_b^{k +1} n.$$"""

import json
from fractions import Fraction

record_id = "SE_cs_1957__a2388"
verdict = "CONFIRMED"
notes = ("Confirmed exactly at a=1, b=4, n=2, k=1: log_4(a)=0, "
         "log_4(n)=1/2, and log_4(n-1)=0; the one-term sum is 1, so "
         "the left side is 1/2 while the right side is 1/4. The refuted "
         "exact equality is substantive, not plainly a typo: the finite "
         "sum does not in general equal the asserted extra logarithmic factor.")

def nonnegative_integer_power(base, exponent):
    if not isinstance(exponent, int) or exponent < 0:
        raise AssertionError("invalid exponent")
    result = 1
    for _ in range(exponent):
        result *= base
    return result

a = 1
b = 4
n = 2
k = 1

if a != 1 or b <= 1 or n <= 1:
    raise AssertionError("witness preconditions failed")

log_b_a = Fraction(0, 1)
if nonnegative_integer_power(b, 0) != a:
    raise AssertionError("logarithm of a was not established")

log_b_n = Fraction(1, 2)
if nonnegative_integer_power(n, 2) != b:
    raise AssertionError("logarithm of n was not established")

log_b_n_minus_1 = Fraction(0, 1)
if n - 1 != nonnegative_integer_power(b, 0):
    raise AssertionError("sum bound was not established")
if log_b_n_minus_1.denominator != 1 or log_b_n_minus_1.numerator < 0:
    raise AssertionError("sum bound is not a nonnegative integer")

base_to_log_a = nonnegative_integer_power(b, log_b_a.numerator)
ratio = Fraction(a, base_to_log_a)
term = Fraction(1, 1)
geometric_sum = Fraction(0, 1)
for _ in range(log_b_n_minus_1.numerator + 1):
    geometric_sum += term
    term *= ratio

n_factor = Fraction(nonnegative_integer_power(n, log_b_a.numerator), 1)
lhs = n_factor * nonnegative_integer_power(log_b_n, k) * geometric_sum
rhs = n_factor * nonnegative_integer_power(log_b_n, k + 1)

if lhs != Fraction(1, 2) or rhs != Fraction(1, 4) or lhs == rhs:
    raise AssertionError("reported refutation was not independently reproduced")

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes},
                 separators=(",", ":")))
