# P30: check of the witness supplied by the critic's response.
# Witness: delta = 0.1, n = 100. Claim under test (lines 249-258):
#   Pr[X > (1+delta) 2n] <= exp(-n * D), D = KL( Bernoulli(1/(1+delta)) || Bernoulli(1/2) ).
# Response: true tail about 0.4, claimed bound about 1.5e-17 -> inequality violated.
from fractions import Fraction as F
from math import comb, log, exp

delta = F(1, 10)
n = 100
thresh = (1 + delta) * 2 * n            # (1+delta)*2n
print("threshold (1+delta)*2n =", thresh, "=", float(thresh))
assert thresh == 220

# --- the claimed bound: D = q log(2q) + (1-q) log(2(1-q)), q = 1/(1+delta)
q = 1 / (1 + float(delta))
Dkl = q * log(2 * q) + (1 - q) * log(2 * (1 - q))
print(f"q = 1/(1+delta) = {q:.6f}   D = KL(Bern(q)||Bern(1/2)) = {Dkl:.6f}")
print(f"claimed bound exp(-n D) = {exp(-n * Dkl):.3e}   (response says about 1.5e-17)")

# --- the source's own derived bound, for comparison: ((1+d)^{2(1+d)} / (1+2d)^{1+2d})^n = exp(-n I)
d = float(delta)
I = (1 + 2 * d) * log(1 + 2 * d) - 2 * (1 + d) * log(1 + d)
print(f"rate of the source's own final bound: I = {I:.6f}  -> exp(-n I) = {exp(-n * I):.4f}")
print(f"D > I ?  {Dkl > I}   (so the KL form asserts a strictly stronger bound than the one derived)")

# --- the TRUE tail probability, exactly: X = number of tosses for the 100th head, so
#     X > 220  <=>  at most 99 heads in the first 220 tosses  <=>  Bin(220,1/2) <= 99
num = sum(comb(220, j) for j in range(0, 100))
true_p = F(num, 2 ** 220)
print(f"exact Pr[X > 220] = Pr[Bin(220,1/2) <= 99] = {float(true_p):.6f}")
print(f"claimed bound                                = {exp(-n * Dkl):.3e}")
print("inequality Pr <= exp(-n D) holds ?", float(true_p) <= exp(-n * Dkl))
assert float(true_p) > exp(-n * Dkl)
ratio = log(float(true_p)) - (-n * Dkl)
print(f"=> violated by a factor of about e^{ratio:.1f} (~{exp(ratio):.1e}): line 251's bound is FALSE here.")

# --- note on the response's own numbers
print()
print("note: the response's 'true tail probability about 0.4' is the exp(-n I) rate approximation")
print(f"      ({exp(-n*I):.4f}); the exact value is {float(true_p):.4f}. Either way it dwarfs the claimed bound.")

# --- and the sanity check that at delta = 1 the KL form degenerates (D = 0), the tell-tale sign
q1 = 1 / 2.0
print(f"at delta = 1: q = {q1}, D = {q1*log(2*q1) + (1-q1)*log(2*(1-q1)):.6f} (identically 0), while")
print(f"      the source's own rate is I = {3*log(3) - 4*log(2):.6f} > 0.")
