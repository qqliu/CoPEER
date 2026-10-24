# P26: check exactly the supplied witness for line 15 ("H_1 cap N_2 normal in H_1"):
# "In G=S_4, letting H_1=S_3 (permutations of 1,2,3), H_2=<(12),(34)>, and N_2=<(12)>, we have
#  N_2 <| H_2 but H_1 cap N_2 = <(12)> is not normal in H_1."
from itertools import permutations

n = 4
S4 = [p for p in permutations(range(1, n + 1))]          # p[i-1] = image of i
def mul(a, b): return tuple(a[b[i] - 1] for i in range(n))   # (a o b)(i) = a(b(i))
def inv(a):
    r = [0] * n
    for i, v in enumerate(a, start=1): r[v - 1] = i
    return tuple(r)
e = (1, 2, 3, 4)
def cyc(*pairs):                                          # build a permutation from a 2-cycle list
    img = list(range(1, n + 1))
    for (x, y) in pairs: img[x - 1], img[y - 1] = y, x
    return tuple(img)
t12, t34 = cyc((1, 2)), cyc((3, 4))

def closure(gens):
    S = {e}
    while True:
        new = {mul(a, b) for a in S for b in S} | {inv(a) for a in S} | set(gens)
        if new <= S: return S
        S |= new

def is_subgroup(H):
    return e in H and all(mul(a, b) in H for a in H for b in H) and all(inv(a) in H for a in H)
def is_normal_in(N, H):
    return N <= H and all(mul(mul(h, x), inv(h)) in N for h in H for x in N)

H1 = {p for p in S4 if p[3] == 4}                 # S_3 on {1,2,3}: fixes 4
H2 = closure([t12, t34])
N2 = closure([t12])
print("|G| =", len(S4), " |H_1| =", len(H1), " |H_2| =", len(H2), " |N_2| =", len(N2))
print("H_1, H_2, N_2 are subgroups of G:", is_subgroup(H1), is_subgroup(H2), is_subgroup(N2))
print("H_2 abelian?", all(mul(a, b) == mul(b, a) for a in H2 for b in H2))
print("N_2 normal in H_2 (source hypothesis P10-P12)?", is_normal_in(N2, H2))
I = H1 & N2
print("H_1 cap N_2 =", sorted(I), " = <(12)> ?", I == N2)
print("H_1 cap N_2 normal in H_1 (line 15)?", is_normal_in(I, H1))
bad = [(h, mul(mul(h, x), inv(h))) for h in H1 for x in I if mul(mul(h, x), inv(h)) not in I]
print("a conjugate leaving the set: h =", bad[0][0], " h x h^-1 =", bad[0][1],
      " which is not in H_1 cap N_2")
print()
print("side condition of the source not fixed by the response: some N_1 <| H_1 must exist;")
for cand, name in (({e}, "{e}"), ({p for p in H1 if sum(1 for i in range(3) if p[i] != i + 1) != 2}, "A_3")):
    print("   N_1 =", name, " is a subgroup:", is_subgroup(cand), " normal in H_1:", is_normal_in(cand, H1))
print()
print("line 15 refuted with all of the source's hypotheses in force?",
      is_normal_in(N2, H2) and not is_normal_in(I, H1))
