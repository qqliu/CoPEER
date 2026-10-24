# P25: check exactly the supplied witness for Theorem Th4 (lines 172-184, conclusion on line 181):
# "Take r=0, s=1; then sqrt(1)-sqrt(0)=1 but (0,1) contains no primes."
# Active assumptions: line 171, "an arbitrary interval (r,s), r,s in R, r<s"; line 174, "If r,s in R
# are such that they satisfy" (eqn12) sqrt(s)-sqrt(r) >= 1; conclusion (eqn13) pi(s)-pi(r) >= 1.
from fractions import Fraction

def pi(x):                       # number of primes <= x, x real
    n = int(x // 1)
    c = 0
    for m in range(2, n + 1):
        if all(m % d for d in range(2, int(m ** 0.5) + 1)):
            c += 1
    return c

r, s = Fraction(0), Fraction(1)
# sqrt of 0 and of 1 are exact rationals, so the hypothesis is checked without floating point
sqrt_r, sqrt_s = Fraction(0), Fraction(1)
print("r =", r, " s =", s, "  r < s ?", r < s, "  both real ? yes")
print("sqrt(s) - sqrt(r) =", sqrt_s - sqrt_r, " >= 1 ?  (eqn12)", sqrt_s - sqrt_r >= 1)
print("pi(s) =", pi(s), "  pi(r) =", pi(r), "  pi(s)-pi(r) =", pi(s) - pi(r),
      " >= 1 ?  (eqn13)", pi(s) - pi(r) >= 1)
print("primes strictly inside (0,1):", [m for m in range(2, 2) ])
print()
print("hypothesis holds and conclusion fails ->",
      (sqrt_s - sqrt_r >= 1) and not (pi(s) - pi(r) >= 1))
print()
print("why the source's proof misses this: line 186 assumes 'P_k < r < s < P_{k+1}',")
print("i.e. that a prime lies below r; the least prime is 2, so no such P_k exists for r = 0.")
print("smallest prime =", min(m for m in range(2, 10) if all(m % d for d in range(2, m))),
      "  is there a prime < r = 0 ?", False)
