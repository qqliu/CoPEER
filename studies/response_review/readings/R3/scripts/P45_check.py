# P45: check the witness x = 3*pi/2 against lines 4-5: "It follows that for all n in Z: 2*pi*n < x < 2*pi*n + pi"
from fractions import Fraction as F
import math
xk = F(3, 2)          # x = xk * pi, kept as an exact rational multiple of pi
print("x = (3/2)*pi ; tan(x/2) = tan(3*pi/4) =", math.tan(3*math.pi/4),
      " (exactly -1, since tan(pi - pi/4) = -tan(pi/4))  nonzero ->", abs(math.tan(3*math.pi/4)) > 0.5)
print("source assumption P3/line 2 'tan(x/2) != 0' holds at the witness: True")
print("sin x =", round(math.sin(1.5*math.pi), 12), "so csc x is defined at the witness too")
# is there an integer n with 2n*pi < x < 2n*pi + pi ?  divide by pi: 2n < 3/2 < 2n+1
ok = [n for n in range(-1000, 1001) if F(2*n) < xk < F(2*n+1)]
print("integers n with 2n < 3/2 < 2n+1 (i.e. x in (2*pi*n, 2*pi*n+pi)):", ok, "-> none")
print("nearest cases: n=0 gives (0, pi) i.e. 0 < 1.5 < 1 ->", F(0) < xk < F(1),
      "; n=1 gives (2pi, 3pi) i.e. 2 < 1.5 < 3 ->", F(2) < xk < F(3))
# the literal 'for all n' reading is refuted by a single failing n as well
print("literal 'for all n' reading fails already at n=5:", not (F(10) < xk < F(11)))
# which x do satisfy the conclusion: only the even-indexed intervals; the witness lies in (pi, 2pi)
print("witness lies in (k*pi,(k+1)*pi) with k =", math.floor(float(xk)), "(odd k, an interval the conclusion omits)")
