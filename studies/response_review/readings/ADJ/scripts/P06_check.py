# ADJ check for P06: the critic's witness G = K_{1,3}, checked against the source's own
# definitions: line 85 (e ~ e' iff the endpoints of e,e' span a clique in G), line 123
# (B(G) has the ~-classes as vertices, adjacent when they intersect), line 98 (\kk is
# K_4 minus an edge: a,b,c,d with ab,ac,ad,bc,bd edges and cd a non-edge).
from itertools import combinations

def edges_of(E): return {frozenset(e) for e in E}

def has_diamond(V, E):          # \kk = K_4 - e
    E = edges_of(E)
    for quad in combinations(V, 4):
        for missing in combinations(quad, 2):
            need = {frozenset(p) for p in combinations(quad, 2)} - {frozenset(missing)}
            if need <= E and frozenset(missing) not in E:
                return True, quad, missing
    return False, None, None

def has_K4(V, E):
    E = edges_of(E)
    return any({frozenset(p) for p in combinations(q, 2)} <= E for q in combinations(V, 4))

def block_graph(V, E):
    E = edges_of(E); El = sorted(map(sorted, E))
    def spans_clique(e, f):
        pts = set(e) | set(f)
        return all(frozenset(p) in E for p in combinations(sorted(pts), 2))
    # ~ classes (union-find on the relation of line 85)
    parent = {frozenset(e): frozenset(e) for e in El}
    def find(x):
        while parent[x] != x: x = parent[x]
        return x
    for e, f in combinations([frozenset(x) for x in El], 2):
        if spans_clique(e, f): parent[find(e)] = find(f)
    classes = {}
    for e in [frozenset(x) for x in El]:
        classes.setdefault(find(e), set()).update(e)      # class as a set of vertices (line 88/90)
    cls = sorted(classes.values(), key=lambda s: sorted(s))
    bedges = [(i, j) for i, j in combinations(range(len(cls)), 2) if cls[i] & cls[j]]
    return cls, bedges

def triangle_in(nv, bedges):
    Eb = {frozenset(e) for e in bedges}
    return [t for t in combinations(range(nv), 3)
            if all(frozenset(p) in Eb for p in combinations(t, 2))]

# the critic's witness: the star K_{1,3}, centre a, leaves b, c, d
V = ["a", "b", "c", "d"]; E = [("a", "b"), ("a", "c"), ("a", "d")]
print("G = K_{1,3}:  diamond (K4-e) present?", has_diamond(V, E)[0], "  K4 present?", has_K4(V, E))
cls, bedges = block_graph(V, E)
print("  ~-classes (as vertex sets, per lines 88/90):", [sorted(c) for c in cls])
print("  B(G) edges:", [(sorted(cls[i]), sorted(cls[j])) for i, j in bedges])
tr = triangle_in(len(cls), bedges)
print("  B(G) is K_3:", len(cls) == 3 and len(bedges) == 3, "  triangles in B(G):", tr)

# contrast: the source's intended class L_tf (claw-free AND diamond-free), e.g. a triangle,
# and a path, to show the proposition is fine there - context only, not part of the grade.
for name, (V2, E2) in {"K_3": (["1","2","3"], [("1","2"),("2","3"),("1","3")]),
                       "P_4": (["1","2","3","4"], [("1","2"),("2","3"),("3","4")])}.items():
    c2, b2 = block_graph(V2, E2)
    print("%s: classes %s  B edges %s  triangles %s" %
          (name, [sorted(c) for c in c2], b2, triangle_in(len(c2), b2)))
