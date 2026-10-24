# P40: exact check of the witness: C_4 = v1-v2-v3-v4-v1, S={v1,v3}, T={v2,v4}.
from itertools import combinations
V = [1,2,3,4]
E = [(1,2),(2,3),(3,4),(1,4)]
def delta(Sp):
    Sp = set(Sp)
    return frozenset(e for e in E if (e[0] in Sp) != (e[1] in Sp))
def components(vs, edges):
    vs = list(vs); parent = {v: v for v in vs}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a,b in edges:
        if a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb: parent[ra] = rb
    out = {}
    for v in vs: out.setdefault(find(v), set()).add(v)
    return list(out.values())
S, T = {1,3}, {2,4}
print("cut C = delta(S) =", sorted(delta(S)), "(all four edges)")
print("components of G[S]:", components(S, E), "  components of G[T]:", components(T, E))
S1, T1 = {1}, {2}
C11 = frozenset(e for e in delta(S) if (e[0] in S1 and e[1] in T1) or (e[1] in S1 and e[0] in T1))
print("C_11 (edges S1={v1} to T1={v2}) =", sorted(C11), "  as the response says: the single edge (v1,v2)")
# all cut-sets of the 4-cycle under Definition 1 (delta(S') over nonempty proper S')
cuts = set()
for k in range(1, len(V)):
    for Sp in combinations(V, k):
        cuts.add(delta(Sp))
print("every cut-set of C_4:", sorted(sorted(c) for c in cuts))
print("is C_11 a cut-set (= delta(S') for some partition)?", C11 in cuts)
print("sizes of cut-sets:", sorted({len(c) for c in cuts}), "-> no cut-set of size 1")
# Definition 2's equivalent reading: does deleting C_11 increase the component count?
before = len(components(V, E))
after = len(components(V, [e for e in E if e not in C11]))
print("components before deleting C_11:", before, " after:", after,
      "-> removal increases components?", after > before)
