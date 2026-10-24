# P42: the response's witness x = -pi/2 against lines 4-5
# (from tan(x/2) != 0 the source infers  for all n in Z:  2 pi n < x < 2 pi n + pi)
from fractions import Fraction as F
import math

x_over_pi = F(-1, 2)                 # x = -pi/2, written as a rational multiple of pi
print("x = (%s) pi" % x_over_pi)
print("tan(x/2) = tan(-pi/4) =", math.tan(math.pi * float(x_over_pi) / 2), "  non-zero?",
      abs(math.tan(math.pi * float(x_over_pi) / 2)) > 1e-12, " (exactly -1)")
print("sin(x) =", math.sin(math.pi * float(x_over_pi)), " so csc x is defined")

# 2 pi n < x < 2 pi n + pi  <=>  2n < x/pi < 2n + 1   (exact in rationals)
hits = [n for n in range(-5, 6) if 2 * n < x_over_pi < 2 * n + 1]
print("integers n with 2n < x/pi < 2n+1 :", hits)
print("holds for SOME n?", bool(hits), "   holds for ALL n (what line 4 says)?", len(hits) > 10)
# the interval the witness actually lies in
k = [n for n in range(-5, 6) if 2 * n - 1 < x_over_pi < 2 * n]
print("x lies instead in (2pi n - pi, 2pi n) for n =", k)
