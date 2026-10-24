# P40: check exactly the supplied witness for line 36 ("Claim: Cij is a cut-set"):
# "In a 4-cycle v1-v2-v3-v4-v1 with S={v1,v3} and T={v2,v4}, the set of edges between S_1={v1} and
#  T_1={v2} is exactly the single edge (v1,v2), which is not a cut-set."
# Definition 1 of the source: a cut-set is delta(S') = E(S',T') for a partition V = S' u T', both
# non-empty.  Definition 2: minimal if no proper subset of it is a cut-set of any partition.
from itertools import combinations

V = [1, 2, 3, 4]
E = [frozenset({1, 2}), frozenset({2, 3}), frozenset({3, 4}), frozenset({1, 4})]

def delta(Sp):
    return frozenset(e for e in E if len(e & set(Sp)) == 1)

def components(verts):
    verts = set(verts)
    seen, comps = set(), []
    for v in sorted(verts):
        if v in seen: continue
        stack, comp = [v], set()
        while stack:
            x = stack.pop()
            if x in comp: continue
            comp.add(x)
            for e in E:
                if x in e and (e - {x}) <= verts:
                    stack.extend(e - {x})
        comps.append(sorted(comp)); seen |= comp
    return comps

all_cutsets = set()
for r in range(1, len(V)):
    for Sp in combinations(V, r):
        all_cutsets.add(delta(Sp))
print("every cut-set of the 4-cycle (Definition 1):")
for c in sorted(all_cutsets, key=lambda s: (len(s), sorted(map(sorted, s)))):
    print("   ", sorted(sorted(e) for e in c))

S, T = [1, 3], [2, 4]
print()
print("S =", S, " T =", T, " is a partition with both parts non-empty:", set(S) | set(T) == set(V) and not set(S) & set(T))
print("C = delta(S) =", sorted(sorted(e) for e in delta(S)))
print("components of G[S]:", components(S), "  components of G[T]:", components(T))
S1, T1 = [1], [2]
C11 = frozenset(e for e in delta(S) if len(e & set(S1)) == 1 and len(e & set(T1)) == 1)
print("C_11 (edges from S_1 = {v1} to T_1 = {v2}) =", sorted(sorted(e) for e in C11),
      " size", len(C11))
print("is C_11 a cut-set of some partition?", C11 in all_cutsets)
print("does removing C_11 increase the number of components?",
      len(components(V)), "->", len([c for c in components(V)]),
      "(the 4-cycle minus one edge is still connected)")
# explicit: components after deleting C_11
E = [e for e in E if e not in C11]
print("components of G - C_11:", components(V))
print()
print("line 36 refuted by the supplied witness?", C11 not in all_cutsets)
