# P34: exact check of the witness supplied by the critic's response.
# Witness: G = S_3, P = <(1 2)>, g = (1 2 3), h = (2 3).
# Response: hgP = gP holds, but ghg^{-1} = (1 3) is not in P, so P != ghg^{-1}P,
# refuting line 27's "hgP = gP ... is equivalent to P = ghg^(-1)P".
from itertools import permutations

pts = (1, 2, 3)
# a permutation is a dict on {1,2,3}; composition is the usual right-to-left one: (a*b)(x) = a(b(x))
def perm(d):
    return tuple(d[x] for x in pts)          # image tuple, index 0 -> image of 1
def ap(p, x):
    return p[x - 1]
def mul(a, b):
    return tuple(ap(a, ap(b, x)) for x in pts)
def inv(a):
    r = [0, 0, 0]
    for x in pts:
        r[ap(a, x) - 1] = x
    return tuple(r)
def name(p):
    if p == (1, 2, 3): return "e"
    cyc = []
    seen = set()
    for x in pts:
        if x in seen: continue
        c = [x]; y = ap(p, x); seen.add(x)
        while y != x:
            c.append(y); seen.add(y); y = ap(p, y)
        if len(c) > 1: cyc.append("(" + " ".join(map(str, c)) + ")")
    return "".join(cyc)

S3 = [perm(dict(zip(pts, q))) for q in permutations(pts)]
e  = (1, 2, 3)
g  = perm({1: 2, 2: 3, 3: 1})        # (1 2 3)
h  = perm({1: 1, 2: 3, 3: 2})        # (2 3)
t12 = perm({1: 2, 2: 1, 3: 3})       # (1 2)
P  = {e, t12}                        # <(1 2)>
H  = {e, h}                          # <(2 3)>, a 2-subgroup

print("g =", name(g), " h =", name(h), " P =", {name(x) for x in P}, " H =", {name(x) for x in H})
print("|G| = 6 = 2^1 * 3, p = 2:  |P| =", len(P), "-> P is a Sylow 2-subgroup:", len(P) == 2)
print("H is a 2-subgroup:", len(H) == 2 and all(mul(a, b) in H for a in H for b in H))

def coset(x, K):                       # left coset xK
    return frozenset(mul(x, k) for k in K)

gP  = coset(g, P)
hgP = coset(mul(h, g), P)
print("gP  =", sorted(name(x) for x in gP))
print("hgP =", sorted(name(x) for x in hgP))
print("hgP == gP ?", hgP == gP, "  (so gP is a fixed point of the H-action of line 25)")
fixed = all(coset(mul(k, g), P) == gP for k in H)
print("gP fixed by every element of H ?", fixed)

c1 = mul(mul(g, h), inv(g))            # g h g^{-1}
c2 = mul(mul(inv(g), h), g)            # g^{-1} h g
print("g h g^{-1} =", name(c1), " in P ?", c1 in P)
print("g^{-1} h g =", name(c2), " in P ?", c2 in P)
print("ghg^{-1}P == P ?", coset(c1, P) == frozenset(P))
assert hgP == gP and fixed and c1 not in P and coset(c1, P) != frozenset(P) and c2 in P
print()
print("=> hgP = gP holds while P != g h g^{-1} P: line 27's stated equivalence is FALSE here.")
print("   (the correct conjugate g^{-1} h g IS in P, i.e. the line has the conjugation reversed)")

# sanity: the same computation under the opposite (left-to-right) composition convention
def mulL(a, b):
    return tuple(ap(b, ap(a, x)) for x in pts)
def cosetL(x, K):
    return frozenset(mulL(x, k) for k in K)
print()
print("under the left-to-right convention instead: hgP == gP ?",
      cosetL(mulL(h, g), P) == cosetL(g, P))
