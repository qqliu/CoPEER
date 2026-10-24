# P16: exact check of the witness supplied by the critic's response.
# Witness: S = {a,b} with edge ab; T = {c,d,e} with edge cd and e isolated; plus edges a-c and a-e.
# Line 35 asserts "C_ij = delta(S_i)". Response: C_11 = {ac} but delta(S_1) = {ac, ae}.
from itertools import combinations

V = ["a", "b", "c", "d", "e"]
E = [frozenset(x) for x in [("a", "b"), ("c", "d"), ("a", "c"), ("a", "e")]]
S, T = {"a", "b"}, {"c", "d", "e"}
print("V =", V, " E =", [sorted(e) for e in E], " S =", sorted(S), " T =", sorted(T))
assert S | T == set(V) and not (S & T) and S and T          # a valid cut partition (Definition 1)

def components(verts, edges):
    verts = set(verts); comps = []
    unseen = set(verts)
    adj = {v: set() for v in verts}
    for e in edges:
        x, y = tuple(e)
        if x in verts and y in verts:
            adj[x].add(y); adj[y].add(x)
    while unseen:
        s = unseen.pop(); comp = {s}; st = [s]
        while st:
            a = st.pop()
            for w in adj[a]:
                if w not in comp:
                    comp.add(w); st.append(w); unseen.discard(w)
        comps.append(comp)
    return sorted(comps, key=lambda c: sorted(c))

def delta(A):                                   # edges with exactly one endpoint in A
    return {e for e in E if len(e & set(A)) == 1}

Scomp, Tcomp = components(S, E), components(T, E)
print("components of G[S]:", [sorted(c) for c in Scomp], " p =", len(Scomp))
print("components of G[T]:", [sorted(c) for c in Tcomp], " q =", len(Tcomp))
C = delta(S)
print("C = delta(S) =", sorted(map(sorted, C)))

Cij = {}
for i, Si in enumerate(Scomp, 1):
    for j, Tj in enumerate(Tcomp, 1):
        Cij[(i, j)] = {e for e in C if e & Si and e & Tj}
for key in sorted(Cij):
    print(f"  C_{key} =", sorted(map(sorted, Cij[key])))

S1 = Scomp[0]
d1 = delta(S1)
print("delta(S_1) with S_1 =", sorted(S1), ":", sorted(map(sorted, d1)))
print("C_11 =", sorted(map(sorted, Cij[(1, 1)])), " non-empty:", bool(Cij[(1, 1)]))
print("C_11 == delta(S_1) ?", Cij[(1, 1)] == d1)
assert Cij[(1, 1)] and Cij[(1, 1)] != d1
print("=> line 35's identification C_ij = delta(S_i) is FALSE on this witness (q = 2 > 1).")

# for the record: in this witness C_11 IS nevertheless a bond, so the theorem's content survives
def ncomp(edges):
    return len(components(V, edges))
base = ncomp(E)
rest = [e for e in E if e not in Cij[(1, 1)]]
print()
print("number of components of G:", base, "; after deleting C_11:", ncomp(rest))
proper_cuts = [sub for r in range(1, len(Cij[(1,1)]))
               for sub in combinations(sorted(Cij[(1,1)], key=sorted), r)
               if ncomp([e for e in E if e not in set(sub)]) > base]
print("proper subsets of C_11 that are themselves cuts:", proper_cuts)
print("so C_11 is a bond here:", ncomp(rest) > base and proper_cuts == [])
