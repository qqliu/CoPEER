# P26: exact finite check of the response's witness inside G = S_4.
from itertools import permutations
G = list(permutations(range(4)))            # p as a tuple: i -> p[i]
def mul(p, q): return tuple(p[q[i]] for i in range(4))   # (p*q)(i) = p(q(i))
def inv(p):
    r = [0]*4
    for i, x in enumerate(p): r[x] = i
    return tuple(r)
e = tuple(range(4))
def cyc(*c):                                 # cycle on 1-based points, as in the response
    p = list(range(4))
    for i in range(len(c)):
        p[c[i]-1] = c[(i+1) % len(c)]-1
    return tuple(p)
def gen(gens):
    S = {e}
    while True:
        new = {mul(a, b) for a in S for b in gens} | S
        if new == S: return S
        S = new
def is_subgroup(S): return all(mul(a, inv(b)) in S for a in S for b in S)
def normal_in(N, H): return all(mul(mul(h, n), inv(h)) in N for h in H for n in N)

H1 = gen({cyc(1,2), cyc(1,2,3)})                       # S_3 on {1,2,3}
H2 = gen({cyc(1,2), cyc(3,4)})
N2 = gen({cyc(1,2)})
print("|H1| =", len(H1), " |H2| =", len(H2), " |N2| =", len(N2))
print("H1,H2,N2 subgroups of S_4:", is_subgroup(H1), is_subgroup(H2), is_subgroup(N2),
      " all inside G:", H1 <= set(G) and H2 <= set(G) and N2 <= set(G))
print("H1 = S_3 fixes the point 4:", all(p[3] == 3 for p in H1))
print("N2 <| H2 (the source's hypothesis):", normal_in(N2, H2))
I = H1 & N2
print("H1 cap N2 =", sorted(I), " equals <(12)> :", I == N2)
print("H1 cap N2 <| H1 (line 15's claim):", normal_in(I, H1))
bad = [h for h in H1 if any(mul(mul(h, n), inv(h)) not in I for n in I)]
h = cyc(1,3)
print("explicit failure: (13)(12)(13)^-1 =", mul(mul(h, cyc(1,2)), inv(h)),
      "= (23) as a tuple", cyc(2,3), " in H1 cap N2?", mul(mul(h, cyc(1,2)), inv(h)) in I)
print("number of conjugating elements of H1 that break normality:", len(bad))
# the source's other hypothesis N_1 <| H_1 is not pinned down by the witness; it is satisfiable
print("N1 = {e} <| H1 :", normal_in({e}, H1), " (so the witness extends to the full hypothesis set)")
print("H1 cap N2 <| H1 cap H2 (the correct form of the cited lemma):", normal_in(I, H1 & H2))
