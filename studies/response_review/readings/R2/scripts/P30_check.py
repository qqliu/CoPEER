# P30: the response's witness delta = 0.1, n = 100 against the KL form of the bound
# (lines 249-258): Pr[X > (1+delta) 2n] <= exp(-n * D), D = KL( Bern(1/(1+delta)) || Bern(1/2) ).
from fractions import Fraction as F
from math import comb, log, exp

d = F(1, 10); n = 100
thr = (1 + d) * 2 * n                       # (1+delta)*2n
print("delta =", d, " n =", n, " threshold (1+delta)2n =", thr)

# TRUE probability, exact:  X = sum of n Geom(1/2) on {1,2,...} = trial of the n-th head.
# X > 220  <=>  at most n-1 = 99 heads in the first 220 tosses.
m = int(thr)
assert thr == m
p_true = F(sum(comb(m, j) for j in range(n)), 1) / F(2) ** m
print("Pr[X > 220] exactly = P(Bin(220,1/2) <= 99) =", float(p_true))

# the KL quantity as the source defines it
q = 1 / (1 + float(d)); p = 0.5
D = q * log(q / p) + (1 - q) * log((1 - q) / (1 - p))
print("D( Bern(1/(1+delta)) || Bern(1/2) ) =", D, "   claimed bound exp(-n D) =", exp(-n * D))

# the source's own (correct) optimised bound, for comparison
dd = float(d)
chern = ((1 + dd) ** (2 + 2 * dd) / (1 + 2 * dd) ** (1 + 2 * dd)) ** n
print("source's line-243 bound ((1+d)^{2+2d}/(1+2d)^{1+2d})^n =", chern)

print()
print("claimed KL bound violated?  Pr >", "exp(-nD):", float(p_true) > exp(-n * D))
print("ratio Pr / claimed bound =", float(p_true) / exp(-n * D))
print("NOTE: the response says the true tail probability is 'about 0.4'; the exact value is",
      round(float(p_true), 4), "- 0.4 is in fact the value of the source's own correct bound", round(chern, 4))
