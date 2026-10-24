# P45: check exactly the supplied witness for lines 4-5 ("It follows that forall n in Z:
# 2 pi n < x < 2 pi n + pi"):
# "For x = 3 pi/2, tan(x/2) = tan(3 pi/4) = -1 != 0, yet 3 pi/2 is not in any interval
#  (2 pi n, 2 pi n + pi)."
from fractions import Fraction as F
from math import tan, pi, sin

x_over_pi = F(3, 2)                    # x = (3/2) pi, handled exactly in units of pi
half = x_over_pi / 2                   # x/2 = (3/4) pi
print("x =", x_over_pi, "* pi,  x/2 =", half, "* pi")
print("tan(x/2) numerically =", tan(float(half) * pi), " (exactly -1; 3pi/4 is pi/4 shifted by pi/2)")
print("tan(x/2) != 0 ?", abs(tan(float(half) * pi)) > 1e-9,
      "  and it is defined (x/2 is not an odd multiple of pi/2):", half % 1 != F(1, 2))
print("the source's hypothesis P3 / line 2 (tan(x/2) != 0) is satisfied.")
print("also sin x =", sin(float(x_over_pi) * pi), "!= 0, so csc x is defined at the witness")
print()
inside = [n for n in range(-5, 6) if F(2 * n) < x_over_pi < F(2 * n + 1)]   # units of pi
print("integers n with 2n < 3/2 < 2n+1 (i.e. 2 pi n < x < 2 pi n + pi):", inside)
print("so x lies in NO interval of the form (2 pi n, 2 pi n + pi):", inside == [])
print("for the record, x does lie in (pi, 2 pi), an interval whose left endpoint is an ODD")
print("multiple of pi:", F(1) < x_over_pi < F(2))
print()
print("what tan(x/2) != 0 really gives: x/2 != k pi, i.e. x is not an even multiple of pi;")
print("   is x an even multiple of pi?", x_over_pi % 2 == 0)
print()
print("lines 4-5 refuted by the supplied witness?",
      abs(tan(float(half) * pi)) > 1e-9 and inside == [])
