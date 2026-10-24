# P06: exact check of the witness K_{1,3} against source line 127 ("G kk-free => B(G) in tf"),
# using the source's own definitions: line 85 (e ~ e' iff the endpoints of e,e' span a clique),
# line 90 (classes are treated as vertex sets / cliques), line 123 (B(G): vertices are the classes,
# adjacency when two classes intersect).
from itertools import combinations
def spans_clique(e, f, E):
    vs = set(e) | set(f)
    return all(frozenset(p) in E for p in combinations(sorted(vs), 2))
def classes(V, E):
    Es = sorted(tuple(sorted(e)) for e in E)
    parent = {e: e for e in Es}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in combinations(Es, 2):
        if spans_clique(a, b, E):
            ra, rb = find(a), find(b)
            if ra != rb: parent[ra] = rb
    out = {}
    for e in Es: out.setdefault(find(e), set()).update(e)     # class as its vertex set (line 85/90)
    return list(out.values())
def block_graph(V, E):
    C = classes(V, E)
    edges = [(i, j) for i, j in combinations(range(len(C)), 2) if C[i] & C[j]]
    return C, edges
def has_triangle(n, edges):
    S = {frozenset(e) for e in edges}
    return any(frozenset((a,b)) in S and frozenset((b,c)) in S and frozenset((a,c)) in S
               for a, b, c in combinations(range(n), 3))
def is_diamond_free(V, E):   # kk = K_4 minus an edge (source line 79 and line 98)
    for quad in combinations(sorted(V), 4):
        m = sum(1 for p in combinations(quad, 2) if frozenset(p) in E)
        if m == 5: return False
    return True
# the witness: the star K_{1,3} with centre c and leaves x,y,z
V = ['c','x','y','z']; E = {frozenset(('c','x')), frozenset(('c','y')), frozenset(('c','z'))}
print("K_{1,3}: kk-free (no 4 vertices carrying 5 edges)?", is_diamond_free(V, E))
C, be = block_graph(V, E)
print("~ classes (as vertex sets):", [sorted(s) for s in C], " -> cx ~ cy would need the edge xy, absent")
print("B(K_{1,3}) has", len(C), "vertices and edges", be, "-> complete graph on 3 vertices:", len(be) == 3)
print("B(K_{1,3}) contains a triangle?", has_triangle(len(C), be), " so B(G) is NOT in tf: line 127 fails")
# control: a graph that is both kk-free and claw-free, where the proposition should hold
V2 = ['1','2','3']; E2 = {frozenset(('1','2')), frozenset(('2','3')), frozenset(('1','3'))}
C2, be2 = block_graph(V2, E2)
print("control K_3 (kk-free, claw-free): classes", [sorted(s) for s in C2],
      " B has", len(C2), "vertex(es), triangle?", has_triangle(len(C2), be2))
