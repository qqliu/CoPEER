# P10: check exactly the witness the response supplies: "For x = 1, the left side is 3/4 but the
# right side is 3", for the claimed identity |(x-2)(x+2)|/(4x^2) = |x-2||x+2|/(x^2) (line 13).
from fractions import Fraction as F

def lhs(x):  # |(x-2)(x+2)| / (4 x^2)
    return abs((x - 2) * (x + 2)) / (4 * x * x)

def rhs(x):  # |x-2| |x+2| / (x^2)
    return abs(x - 2) * abs(x + 2) / (x * x)

def true_value(x):  # what line 13's chain starts from: |1/x^2 - 1/4|
    return abs(F(1, 1) / (x * x) - F(1, 4))

x = F(1)
print("x =", x)
print("LHS |(x-2)(x+2)|/(4x^2) =", lhs(x), "=", float(lhs(x)))
print("RHS |x-2||x+2|/(x^2)    =", rhs(x), "=", float(rhs(x)))
print("equal?", lhs(x) == rhs(x))
print("the response's stated values 3/4 and 3 reproduce?", lhs(x) == F(3, 4) and rhs(x) == F(3))
print("|1/x^2 - 1/4| at x=1      =", true_value(x), " (matches LHS:", true_value(x) == lhs(x), ")")
print()
# is the failure specific to x=1?  ratio RHS/LHS on a grid of rationals, incl. the delta<=1 window 1<x<3
print("ratio RHS/LHS over sample x (x != 0, x != 2):")
for num, den in [(1,1),(3,2),(5,4),(9,4),(11,4),(5,2),(7,2),(-1,1),(1,2)]:
    x = F(num, den)
    print("  x =", x, " LHS =", lhs(x), " RHS =", rhs(x), " RHS/LHS =", rhs(x)/lhs(x) if lhs(x) else None)
