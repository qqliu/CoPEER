# P10: check the witness x=1 against the last equality of source line 13:
#   |(x-2)(x+2)|/(4x^2)  =  |x-2||x+2|/(x^2)
from fractions import Fraction as F
L = lambda x: abs((x-2)*(x+2)) / (4*x*x)
R = lambda x: abs(x-2)*abs(x+2) / (x*x)
x = F(1)
print("witness x=1: LHS =", L(x), " RHS =", R(x), " equal?", L(x) == R(x), " (response says 3/4 vs 3)")
print("ratio RHS/LHS at x=1:", R(x)/L(x))
# is the failure specific to x=1, or does the dropped factor 4 make the identity fail generally?
xs = [F(1), F(3,2), F(2), F(5,2), F(9,4), F(3), F(-1), F(10)]
print("x : (LHS, RHS, equal?)", {str(t): (str(L(t)), str(R(t)), L(t) == R(t)) for t in xs})
print("equal only where both sides vanish (x = 2):", [str(t) for t in xs if L(t) == R(t)])
