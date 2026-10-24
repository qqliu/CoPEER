# ADJ check for P31: exact permutation arithmetic on the critic's supplied witness,
# taken exactly as supplied.  Convention (s*t)(x) = s(t(x)), the one the response uses.
from itertools import permutations

E = list(permutations((1, 2, 3)))            # perm p as tuple: p[i-1] = image of i
def mul(s, t): return tuple(s[t[i] - 1] for i in range(3))
def inv(s):
    r = [0, 0, 0]
    for i in range(3): r[s[i] - 1] = i + 1
    return tuple(r)
e  = (1, 2, 3)
t12, t13, t23 = (2, 1, 3), (3, 2, 1), (1, 3, 2)
c123 = (2, 3, 1)                              # 1->2,2->3,3->1
name = {e: "e", t12: "(12)", t13: "(13)", t23: "(23)", c123: "(123)", inv(c123): "(132)"}
def nm(s): return name[s]
def coset(g, P): return frozenset(mul(g, p) for p in P)

P = frozenset({e, t12})                       # <(12)>, a Sylow 2-subgroup of S3 (|S3|=6=2*3)
g, h = c123, t23                              # the response's g and h
H_response = frozenset({e, t13})              # the H the response names
print("P =", sorted(map(nm, P)), " |S3|=6=2^1*3 so P is Sylow-2:", len(P) == 2)
print("response's H =", sorted(map(nm, H_response)), "  h =", nm(h), "  h in H:", h in H_response)

print("hg =", nm(mul(h, g)))
print("hgP =", sorted(map(nm, coset(mul(h, g), P))), " gP =", sorted(map(nm, coset(g, P))),
      " equal:", coset(mul(h, g), P) == coset(g, P))
ghg = mul(mul(g, h), inv(g))
print("g h g^-1 =", nm(ghg), " in P:", ghg in P, "   [response says (13), not in P]")
ginvhg = mul(mul(inv(g), h), g)
print("g^-1 h g =", nm(ginvhg), " in P:", ginvhg in P, "   [the correct direction]")

# is the response's own H consistent with the source's context at line 25-27?
gP = coset(g, P)
print("gP fixed by response's H:",
      all(frozenset(mul(x, c) for c in gP) == gP for x in H_response))
print("gP fixed by <h> = {e,(23)}:",
      all(frozenset(mul(x, c) for c in gP) == gP for x in frozenset({e, h})))
# full check: which (H, coset) pairs are fixed points, and where the implication fails
sub2 = [frozenset({e, x}) for x in (t12, t13, t23)]
cosets = {coset(x, P) for x in E}
print("\nall 2-subgroups H, their fixed cosets, and the two conjugates for each h in H:")
for H in sub2:
    for C in sorted(cosets, key=lambda s: sorted(map(nm, s))):
        if all(frozenset(mul(x, c) for c in C) == C for x in H):
            rep = [x for x in E if coset(x, P) == C][0]
            for x in H:
                if x == e: continue
                print("  H=%s fixed coset %sP=%s : g h g^-1 = %s in P? %s | g^-1 h g = %s in P? %s"
                      % (sorted(map(nm, H)), nm(rep), sorted(map(nm, C)),
                         nm(mul(mul(rep, x), inv(rep))), mul(mul(rep, x), inv(rep)) in P,
                         nm(mul(mul(inv(rep), x), rep)), mul(mul(inv(rep), x), rep) in P))
