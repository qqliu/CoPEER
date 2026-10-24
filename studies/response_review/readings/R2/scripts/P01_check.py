# P01: check the response's witness k=1, P_1=2 for the line-144 parity claim
# "floor(P_k + 2*sqrt(P_k)) + 1 is an even number for any k"
# Exact integer arithmetic: for integer P>0, floor(P + 2*sqrt(P)) = P + isqrt(4*P)
from math import isqrt

def upper(P):            # floor(P + 2*sqrt(P)) + 1, exactly
    return P + isqrt(4 * P) + 1

def is_prime(n):
    if n < 2: return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0: return False
    return True

P1 = 2
v = upper(P1)
print("P_1 =", P1, " floor(P+2*sqrt(P))+1 =", v,
      " even?", v % 2 == 0, " prime?", is_prime(v))
# sanity on the float value the response quotes
print("float check: 2 + 2*2**0.5 =", 2 + 2*2**0.5)
# the first few primes, for context on how general the failure is
primes = [p for p in range(2, 60) if is_prime(p)]
print("k, P_k, value, even?:", [(i+1, p, upper(p), upper(p) % 2 == 0) for i, p in enumerate(primes[:8])])
