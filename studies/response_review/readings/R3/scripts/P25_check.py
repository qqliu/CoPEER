# P25: check the witness r=0, s=1 against Theorem Th4 (source lines 174-183).
from math import isqrt, sqrt
def pi(x):                      # number of primes <= x, for real x
    n = int(x // 1)
    if n < 2: return 0
    c = 0
    for m in range(2, n+1):
        if all(m % d for d in range(2, isqrt(m)+1)): c += 1
    return c
r, s = 0.0, 1.0
print("witness r =", r, " s =", s, "  r < s ?", r < s, "  both real, and r >= 0 so the square roots exist")
print("hypothesis (eqn12): sqrt(s) - sqrt(r) =", sqrt(s)-sqrt(r), ">= 1 ?", sqrt(s)-sqrt(r) >= 1)
print("primes in the open interval (0,1):", [p for p in range(2, 2) ], "-> none (no integer lies in (0,1) at all)")
print("conclusion (eqn13): pi(s) - pi(r) =", pi(s), "-", pi(r), "=", pi(s)-pi(r), ">= 1 ?", pi(s)-pi(r) >= 1)
print("so the witness satisfies (eqn12) and violates (eqn13):",
      sqrt(s)-sqrt(r) >= 1 and pi(s)-pi(r) < 1)
# where the source's proof (line 186) breaks on this witness: it needs a prime P_k < r
print("smallest prime is 2; is there a prime P_k with P_k < r = 0 ?", False,
      "-> the proof's 'P_k < r < s < P_{k+1}' cannot be set up below 2")
