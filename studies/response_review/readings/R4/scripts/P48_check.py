# P48: exact finite check of the witness supplied by the critic's response.
# Witness: G = the claw K_{1,3}.  Response: G is kk-free but B(G) is a triangle, so B(G) is not
# triangle-free, refuting line 127 ("Let G be a kk-free graph. Then B(G) in tf").
# All definitions taken from the packet's source:
#   line 47 : kk = the graph on four vertices with five edges (K4 minus an edge)
#   line 85 : e ~ e' iff the endpoints of e and e' span a clique in G
#   lines 85, 90 : a ~-class is treated as a SET OF VERTICES (a clique); two classes meet in
#                  at most one vertex -- so the intersection in the next definition is of vertex sets
#   line 123: B(G) = ({C(e) : e in E(G)}, {(C(e),C(e')) : C(e) cap C(e') nonempty})
from itertools import combinations

def edges_of(E):
    return {frozenset(e) for e in E}

def has_kk(V, E):
    """does G embed kk = 4 vertices with 5 edges (as a subgraph on 4 vertices)?"""
    for S in combinations(V, 4):
        cnt = sum(1 for e in E if set(e) <= set(S))
        if cnt >= 5:
            return True
    return False

def is_clique(S, E):
    return all(frozenset({u, v}) in E for u, v in combinations(S, 2))

def classes(V, E):
    """~ classes of edges, then each class rendered as the set of its endpoints (source lines 85, 90)"""
    E = sorted(E, key=lambda e: sorted(e))
    rel = {}
    def find(x):
        while rel.get(x, x) != x:
            x = rel[x]
        return x
    def uni(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            rel[rx] = ry
    for e in E:
        rel.setdefault(e, e)
    for e, f in combinations(E, 2):
        if is_clique(set(e) | set(f), set(E)):
            uni(e, f)
    buckets = {}
    for e in E:
        buckets.setdefault(find(e), []).append(e)
    return [(sorted(frozenset().union(*b)), [sorted(x) for x in b]) for b in buckets.values()]

def block_graph(V, E):
    cl = classes(V, E)
    verts = [frozenset(c[0]) for c in cl]
    ed = [(i, j) for i, j in combinations(range(len(verts)), 2) if verts[i] & verts[j]]
    return cl, verts, ed

def has_triangle(n, ed):
    s = {frozenset(e) for e in ed}
    return any(frozenset({a, b}) in s and frozenset({b, c}) in s and frozenset({a, c}) in s
               for a, b, c in combinations(range(n), 3))

# ---- the response's witness: the claw K_{1,3}, centre a, leaves b,c,d -------------------
V = ["a", "b", "c", "d"]
E = edges_of([("a", "b"), ("a", "c"), ("a", "d")])
print("G = claw K_{1,3}: V =", V, " E =", sorted(map(sorted, E)))
print("G embeds kk (4 vertices, 5 edges) ?", has_kk(V, E), " -> G is kk-free:", not has_kk(V, E))
cl, verts, ed = block_graph(V, E)
print("~ classes (endpoint set, member edges):")
for vs, es in cl:
    print("   ", vs, "<-", es)
print("B(G): vertices =", [sorted(v) for v in verts], " edges =", ed)
print("B(G) is complete on 3 vertices ?", len(verts) == 3 and len(ed) == 3)
print("B(G) contains a triangle ?", has_triangle(len(verts), ed), " -> B(G) in tf:", not has_triangle(len(verts), ed))
assert not has_kk(V, E) and len(verts) == 3 and has_triangle(len(verts), ed)
print("=> line 127 is FALSE at G = K_{1,3}: kk-free, yet B(G) = K_3 is not triangle-free.")

# ---- why the source's own proof (line 130) misses it: the three pairwise intersections
#      of the classes are all the single vertex 'a', so the v_xy are NOT distinct.
inters = {(i, j): sorted(verts[i] & verts[j]) for i, j in combinations(range(len(verts)), 2)}
print()
print("pairwise intersections of the three classes:", inters)
print("all equal to the single centre vertex, so the 'distinct vertices v_xy' of line 130 do not exist")

# ---- convention note: if a class were read as its set of EDGES, classes would be disjoint by
#      construction and B(G) would have no edges at all; the source's lines 85 and 90 speak of a
#      class containing vertices and of classes sharing a vertex, which is the reading used above.
