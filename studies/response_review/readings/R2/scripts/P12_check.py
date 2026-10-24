# P12: the response's witness x = 1 against line 13's final equality
#   |1/x^2 - 1/4|  =?=  |x-2| |x+2| / x^2      (the source drops the factor 4)
from fractions import Fraction as F
def lhs(x): return abs(F(1, 1) / x**2 - F(1, 4))
def rhs_source(x): return abs(x - 2) * abs(x + 2) / x**2        # line 13 as written
def rhs_correct(x): return abs(x - 2) * abs(x + 2) / (4 * x**2) # the value it should equal
for x in (F(1), F(3, 2), F(5, 2), F(3)):
    print("x =", x, " |1/x^2-1/4| =", lhs(x),
          " line-13 RHS =", rhs_source(x), " equal?", lhs(x) == rhs_source(x),
          " | with the 4 restored:", rhs_correct(x), " equal?", lhs(x) == rhs_correct(x))
x = F(1)
print("\nsupplied witness x = 1:", float(lhs(x)), "vs", float(rhs_source(x)),
      " ratio =", rhs_source(x) / lhs(x))
