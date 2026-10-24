# P06: check the supplied witness G = K_{1,3} against the source's definitions.
# Source defs used:
#   line 47: \kk = the graph on four vertices with five edges (K_4 minus an edge, "diamond")
#   line 85: e ~ e' iff the endpoints of e and e' span a clique in G
#   line 123: B(G) = ({C(e)}, {(C(e),C(e')) : C(e) cap C(e') != empty}),
#             classes read as vertex sets (the clique  U e/~ ), which is the reading
#             forced by line 90 and by the proof at line 130 ("distinct vertices v_xy in C(x) cap C(y)")
#   line 45: \tf = all triangle-free graphs
from itertools import combinations

def spans_clique(G_edges, verts):
    return all(frozenset(p) in G_edges for p in combinations(sorted(verts), 2))

def classes(V, E):
    E = [frozenset(e) for e in E]
    Eset = set(E)
    # ~ : e ~ e' iff endpoints of e,e' span a clique
    parent = {e: e for e in E}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for e1, e2 in combinations(E, 2):
        if spans_clique(Eset, set(e1) | set(e2)):
            union(e1, e2)
    cls = {}
    for e in E:
        cls.setdefault(find(e), set()).update(e)   # class as vertex set (union of its edges)
    return list(cls.values())

def is_equiv_relation_ok(V, E):
    # sanity: check ~ as defined is transitive on this G (Prop line 85 needs \kk-freeness)
    E = [frozenset(e) for e in E]; Eset = set(E)
    rel = {(a, b) for a in E for b in E if spans_clique(Eset, set(a) | set(b))}
    return all(((a, c) in rel) for a in E for b in E for c in E
               if (a, b) in rel and (b, c) in rel)

def has_diamond(V, E):
    Eset = {frozenset(e) for e in E}
    for quad in combinations(V, 4):
        m = sum(1 for p in combinations(quad, 2) if frozenset(p) in Eset)
        if m == 5:
            return True
    return False

def block_graph(V, E):
    C = classes(V, E)
    n = len(C)
    adj = [[False] * n for _ in range(n)]
    for i, j in combinations(range(n), 2):
        if C[i] & C[j]:
            adj[i][j] = adj[j][i] = True
    return C, adj

def has_triangle(n, adj):
    return any(adj[i][j] and adj[j][k] and adj[i][k] for i, j, k in combinations(range(n), 3))

# The witness the response supplies verbatim: "The star graph K_{1,3}"
V = ['a', 'b', 'c', 'd']
E = [('a', 'b'), ('a', 'c'), ('a', 'd')]

print("G = K_{1,3}, V =", V, "E =", E)
print("G contains a diamond (K_4 minus an edge)? ", has_diamond(V, E))
print("~ is transitive on E(G)?                   ", is_equiv_relation_ok(V, E))
C, adj = block_graph(V, E)
print("~ classes as vertex sets (cliques):        ", [sorted(c) for c in C])
print("B(G) edges:", [(sorted(C[i]), sorted(C[j]))
                      for i in range(len(C)) for j in range(i + 1, len(C)) if adj[i][j]])
print("B(G) is a triangle (K_3)?                  ",
      len(C) == 3 and all(adj[i][j] for i in range(3) for j in range(i + 1, 3)))
print("B(G) triangle-free, i.e. B(G) in \\tf?      ", not has_triangle(len(C), adj))
print()
print("Proposition at line 127 says: G \\kk-free  =>  B(G) in \\tf.")
print("Witness satisfies hypothesis and fails conclusion? ",
      (not has_diamond(V, E)) and has_triangle(len(C), adj))
