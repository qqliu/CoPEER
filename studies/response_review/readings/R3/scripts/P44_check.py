# P44: check the witness n=2, x=1, y=1 against source line 25:
#   x + y  =  sum_{i=0}^{1} C(n,i) x^i y^(n-i)
from math import comb
from fractions import Fraction as F
def rhs(n, x, y): return sum(comb(n, i) * x**i * y**(n-i) for i in range(0, 2))
n, x, y = 2, 1, 1
print("witness n=2, x=1, y=1:  LHS = x+y =", x+y,
      "  RHS = C(2,0)*1^0*1^2 + C(2,1)*1^1*1^1 =", rhs(n, x, y))
print("equal?", x+y == rhs(n, x, y), " (response says 2 vs 3)")
print()
print("for which n does line 25 hold at x=y=1?  n : (LHS, RHS)",
      {m: (2, rhs(m, 1, 1)) for m in range(0, 6)})
print("holds only at n =", [m for m in range(0, 50) if 2 == rhs(m, 1, 1)])
