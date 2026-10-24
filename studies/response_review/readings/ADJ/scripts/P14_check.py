# ADJ check for P14: exact arithmetic on the critic's supplied witness (delta = 1),
# using only the source's own final expression (lines 242-244 / 229-230) and the
# source's own definition of D (lines 254-258).
from fractions import Fraction
import math

d = Fraction(1)                      # the critic's delta = 1
num = (1 + d) ** (2 * (1 + d))       # (1+delta)^{2(1+delta)}
den = (1 + 2 * d) ** (1 + 2 * d)     # (1+2delta)^{1+2delta}
print("delta =", d, " (1+d)^(2(1+d)) =", num, " (1+2d)^(1+2d) =", den, " base =", Fraction(num, den))
# the alternative printed form at lines 213-214: (1+delta)^{2+2delta}/(1+2delta)^{1+2delta}
print("alt form (2+2d exponent):", Fraction((1 + d) ** (2 + 2 * d), den), " identical:",
      Fraction(num, den) == Fraction((1 + d) ** (2 + 2 * d), den))

def kl_bern(p, q):
    t = 0.0
    if p > 0: t += p * math.log(p / q)
    if p < 1: t += (1 - p) * math.log((1 - p) / (1 - q))
    return t

p = Fraction(1, 1 + d)               # Bernoulli(1/(1+delta)) as the source defines it
print("Bernoulli(1/(1+delta)) parameter =", p, "  vs Bernoulli(1/2)")
print("D = KL(Bern(p) || Bern(1/2)) =", kl_bern(float(p), 0.5),
      "   reversed:", kl_bern(0.5, float(p)))
print("exp(-n*D) = 1 for every n;  source's own bound base =", Fraction(num, den),
      "= %.6f" % float(Fraction(num, den)))
print("equality claimed by lines 248-258 fails for every n>=1:",
      all(Fraction(num, den) ** n != 1 for n in range(1, 6)))
# what D would have to be for the two expressions to agree
print("D that would reproduce the bound: ln(den/num) =", math.log(float(Fraction(den, num))))
