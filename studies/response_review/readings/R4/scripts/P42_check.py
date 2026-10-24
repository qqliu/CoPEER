# P42: exact check of the witness supplied by the critic's response.
# Witness: x = -pi/2.  Response: tan(x/2) = -1 is nonzero, but x is in no interval
# (2 pi n, 2 pi n + pi), "let alone all of them".
from fractions import Fraction as F

# work in units of pi with exact rationals: x = -1/2 (i.e. x = -pi/2)
x = F(-1, 2)

# (a) tan(x/2) = tan(-pi/4) = -1 != 0 : exact known value, checked numerically too
import math
val = math.tan(float(x) * math.pi / 2)
print("x = -pi/2 ; x/2 = -pi/4 ; tan(x/2) numerically =", val, " (exact value -1, nonzero)")
assert abs(val + 1) < 1e-12

# (b) is there an integer n with 2 pi n < x < 2 pi n + pi ?  In units of pi: 2n < -1/2 < 2n + 1
ns = [n for n in range(-1000, 1001) if F(2 * n) < x < F(2 * n + 1)]
print("integers n in [-1000,1000] with 2n < -1/2 < 2n+1 :", ns)
# exact argument, no search needed: 2n < -1/2 => n <= -1 ; -1/2 < 2n+1 => 2n > -3/2 => n >= 0
print("exact: 2n < -1/2 forces n <= -1 (n integer); -1/2 < 2n+1 forces n >= 0 - incompatible")
assert ns == []
print("=> x = -pi/2 satisfies tan(x/2) != 0 yet lies in NO interval (2 pi n, 2 pi n + pi);")
print("   a fortiori the 'for all n in Z' claim of lines 4-5 fails at this x.")

# (c) for completeness: the 'for all n' form is unsatisfiable for every x, since the intervals
# are pairwise disjoint; e.g. no x lies in both (0,pi) and (2pi,3pi).
print()
print("intervals (2n, 2n+1) in units of pi are pairwise disjoint, so no x lies in all of them:")
print("   n=0 -> (0,1)pi ; n=1 -> (2,3)pi ; overlap:", max(0, min(1, 3) - max(0, 2)) == 0)
