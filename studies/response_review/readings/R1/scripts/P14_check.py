# P14: check exactly the supplied witness for the "equivalently" claim of lines 248-258:
# "For delta=1, the bound evaluates to (16/27)^n, whereas the specified KL divergence is
#  D(1/2 || 1/2) = 0, which would give a bound of 1."
# Source objects: the derived bound per factor, lines 242-243,
#   B(delta) = (1+delta)^{2(1+delta)} / (1+2delta)^{1+2delta}
# and the claimed reformulation, lines 249-258, exp(-n D) with D the KL divergence between a
# Bernoulli(1/(1+delta)) and a Bernoulli(1/2).
from fractions import Fraction as F
from math import log, exp

def B(d):                                  # per-factor value of the derived bound
    return (1 + d) ** (2 * (1 + d)) / (1 + 2 * d) ** (1 + 2 * d)

def D(d):                                  # KL(Bern(1/(1+delta)) || Bern(1/2)), nats
    a = 1.0 / (1 + d)
    return log(2.0) + a * log(a) + (1 - a) * log(1 - a)

# delta = 1, exactly
num, den = F(2) ** 4, F(3) ** 3            # (1+1)^{2*2} = 2^4 ; (1+2)^{1+2} = 3^3
print("delta = 1:  per-factor derived bound = (1+d)^{2(1+d)}/(1+2d)^{1+2d} =", num / den,
      "=", float(num / den))
print("            response says (16/27)^n; per-factor 16/27 matches?", num / den == F(16, 27))
a = F(1, 2)                                 # Bernoulli(1/(1+delta)) = Bernoulli(1/2) at delta = 1
print("            Bernoulli(1/(1+delta)) parameter =", a, "; reference Bernoulli(1/2) parameter = 1/2")
print("            KL divergence between two identical Bernoulli(1/2) =", 0, "exactly")
print("            so exp(-n*D) =", 1, "for every n, while the derived bound is (16/27)^n < 1")
print("            the two expressions agree at delta = 1 ?", False)
print()
print(" delta   per-factor bound B    exp(-D)          equal?")
for d in (0.25, 0.5, 1.0, 2.0, 5.0):
    print("%6.2f   %16.10f   %14.10f   %s" % (d, B(d), exp(-D(d)), abs(B(d) - exp(-D(d))) < 1e-12))
print()
print("-ln B(1) =", -log(B(1.0)), " while D(1) =", D(1.0),
      " (the exponents differ, so the claimed reformulation is not the same bound)")
