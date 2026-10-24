# P34: the response's witness in S_3: P = <(1 2)>, g = (1 2 3), h = (2 3), against line 27's
# first equivalence  hgP = gP  <=>  P = g h g^{-1} P.
from itertools import permutations
S3 = list(permutations((1, 2, 3)))          # tuple t means i -> t[i-1]
def mul(a, b): return tuple(a[b[i] - 1] for i in range(3))   # (a*b)(x) = a(b(x))
def inv(a):
    r = [0, 0, 0]
    for i, v in enumerate(a): r[v - 1] = i + 1
    return tuple(r)
e  = (1, 2, 3)
t12 = (2, 1, 3)      # (1 2)
t23 = (1, 3, 2)      # (2 3)
t13 = (3, 2, 1)      # (1 3)
c123 = (2, 3, 1)     # (1 2 3): 1->2, 2->3, 3->1

P = {e, t12}
H = {e, t23}
g, h = c123, t23
print("|S_3| = 6 = 2^1 * 3, p = 2, m = 3, p does not divide m:", 6 % 2 == 0 and 3 % 2 == 1)
print("P is a Sylow 2-subgroup?", len(P) == 2 and all(mul(x, y) in P for x in P for y in P))
print("H is a 2-subgroup?", len(H) == 2 and all(mul(x, y) in H for x in H for y in H))

def coset(x, K): return frozenset(mul(x, k) for k in K)
print("\nhgP == gP ?", coset(mul(h, g), P) == coset(g, P))
print("is gP a fixed point of the H-action (line 25)?",
      all(coset(mul(x, g), P) == coset(g, P) for x in H))
ghg = mul(mul(g, h), inv(g))
gig = mul(mul(inv(g), h), g)
print("g h g^{-1} =", ghg, "= (1 3)?", ghg == t13, " in P?", ghg in P)
print("P == (g h g^{-1}) P ?", P == coset(ghg, P))
print("g^{-1} h g =", gig, "= (1 2)?", gig == t12, " in P?", gig in P, " (this is the correct conjugate)")
print("\nline 27's equivalence holds at this (g,h)?",
      (coset(mul(h, g), P) == coset(g, P)) == (P == coset(ghg, P)))
