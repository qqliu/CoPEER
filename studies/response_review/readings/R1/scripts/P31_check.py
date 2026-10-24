# P31: check exactly the supplied witness for line 27's equivalence:
# "In G = S3, let P = <(12)>, H = <(13)>, g = (123) and h = (23); we have hgP = gP but
#  ghg^{-1} = (13) not in P."
from itertools import permutations

S3 = [p for p in permutations((1, 2, 3))]
def mul(a, b): return tuple(a[b[i] - 1] for i in range(3))     # (a o b)(i) = a(b(i))
def inv(a):
    r = [0, 0, 0]
    for i, v in enumerate(a, start=1): r[v - 1] = i
    return tuple(r)
e = (1, 2, 3)
t12, t13, t23 = (2, 1, 3), (3, 2, 1), (1, 3, 2)
c123 = (2, 3, 1)          # 1->2, 2->3, 3->1
def gen(*gs):
    S = {e}
    while True:
        new = {mul(a, b) for a in S for b in S} | {inv(a) for a in S} | set(gs)
        if new <= S: return S
        S |= new
def coset(x, P): return frozenset(mul(x, p) for p in P)

P = gen(t12)
H_named = gen(t13)        # the H the response names
g, h = c123, t23          # the g and h the response supplies
print("|G| = 6 = 2*3, p = 2, m = 3, p does not divide m:", 6 % 2 == 0 and 3 % 2 == 1)
print("P =", sorted(P), " |P| = 2 = p^r, so P is a Sylow 2-subgroup:", len(P) == 2)
print("gP  =", sorted(coset(g, P)))
print("hgP =", sorted(coset(mul(h, g), P)))
print("hgP = gP ?", coset(mul(h, g), P) == coset(g, P))
ghg = mul(mul(g, h), inv(g))
ghg_other = mul(mul(inv(g), h), g)
print("g h g^-1 =", ghg, " in P ?", ghg in P, "   (line 27's claim needs this to be True)")
print("g^-1 h g =", ghg_other, " in P ?", ghg_other in P, "   (the correct consequence)")
print("P = (g h g^-1) P ?", coset(ghg, P) == P)
print()
print("the response's H label: h =", h, " in H = <(13)> =", sorted(H_named), "?", h in H_named)
print("is gP fixed by every element of H = <(13)> ?",
      all(coset(mul(x, g), P) == coset(g, P) for x in H_named))
H_fix = gen(h)
print("is gP fixed by every element of <h> = <(23)> =", sorted(H_fix), "?",
      all(coset(mul(x, g), P) == coset(g, P) for x in H_fix),
      " and is <h> a 2-subgroup? order =", len(H_fix))
print()
print("line 27 refuted by the supplied h, g, P:",
      coset(mul(h, g), P) == coset(g, P) and ghg not in P)
