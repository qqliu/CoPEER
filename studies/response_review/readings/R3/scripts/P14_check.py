# P14: check the response's witness delta=1 against the source's two expressions for the bound.
from fractions import Fraction as F
import math
d = F(1)                       # the response's witness delta = 1
# base of the derived bound, lines 213-214 / 242-243: (1+d)^(2+2d) / (1+2d)^(1+2d)
num = (1+d)**int(2+2*d); den = (1+2*d)**int(1+2*d)
base = F(num, 1) / F(den, 1)
print("derived base at delta=1:", num, "/", den, "=", base, "=", float(base))
print("line 242 form (1+d)^(2(1+d)) / (1+2d)^(1+2d):", (1+d)**int(2*(1+d)), "/", (1+2*d)**int(1+2*d))
# the line 249-258 expression: exp(-n D), D = KL( Bernoulli(1/(1+d)) || Bernoulli(1/2) )
p = F(1, 1+d); q = F(1, 2)
print("delta=1 -> Bernoulli(1/(1+delta)) has p =", p, "; other is q =", q)
def kl(p, q):
    p = float(p); q = float(q)
    t = 0.0
    if p > 0: t += p*math.log(p/q)
    if p < 1: t += (1-p)*math.log((1-p)/(1-q))
    return t
D = kl(p, q)
print("D =", D, " -> exp(-n D) =", math.exp(-D), "per factor (i.e. bound 1 for every n)")
print("equal?", abs(float(base) - math.exp(-D)) < 1e-12, " 16/27 =", float(F(16,27)))
