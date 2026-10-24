r"""All graphs are finite, undirected, and simple. A graph is triangle-free if it has no three distinct pairwise adjacent vertices. Let G have vertex set V(G)={v_1,...,v_n}, where n=|V(G)|>=2, and suppose G is triangle-free. Write deg_G(v_i) for the degree of v_i, and let 0 be a symbol distinct from 1,...,n. Construct H with
V(H)={{i,j}: i,j in {1,...,n}, v_i v_j in E(G), and deg_G(v_i)>1} union {{0,i}: i in {1,...,n} and deg_G(v_i)=1},
where two distinct vertices p,q of H are adjacent exactly when p intersect q is nonempty.

Let K_4^- denote the graph on four vertices with five edges. For a K_4^--free graph X and e,e' in E(X), define e~e' when the endpoints of e and e' together span a clique in X. This is an equivalence relation. For e in E(X), let C_X(e) be the clique consisting of all endpoints of edges in the equivalence class of e. Define B(X) to be the graph whose vertices are the distinct cliques C_X(e), e in E(X), with two distinct such cliques adjacent exactly when their intersection is nonempty.

For each i in {1,...,n}, put C_i={p in V(H): i in p}. The claim is that H is K_4^--free; every C_i is one of the vertices C_H(e) of B(H); the C_i are pairwise distinct and exhaust V(B(H)); and the map phi:V(G)->V(B(H)) given by phi(v_i)=C_i is a graph isomorphism. Equivalently, in addition to being a bijection, it satisfies v_i v_j in E(G) if and only if C_i and C_j are adjacent in B(H), for every distinct i,j."""

import json

REPORT = {
    "record_id": "arxiv_1604.01374v4__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid. The refuted statement is substantive as written, not plainly a typo: the construction omits isolated vertices, so the two isolated vertices of G produce equal empty C_i sets and no vertices of B(H).",
}

n = 2
g_vertices = frozenset(range(1, n + 1))
g_edges = frozenset()

assert len(g_vertices) == n
assert n >= 2
assert all(a != b and a in g_vertices and b in g_vertices for a, b in g_edges)
assert all(
    not (
        frozenset((a, b)) in g_edges
        and frozenset((a, c)) in g_edges
        and frozenset((b, c)) in g_edges
    )
    for a in g_vertices
    for b in g_vertices
    for c in g_vertices
    if a < b < c
)

degrees = {
    i: sum(1 for edge in g_edges if i in edge)
    for i in g_vertices
}
assert degrees == {1: 0, 2: 0}

h_vertices_from_edges = {
    frozenset((i, j))
    for i in g_vertices
    for j in g_vertices
    if frozenset((i, j)) in g_edges and degrees[i] > 1
}
h_vertices_from_leaves = {
    frozenset((0, i))
    for i in g_vertices
    if degrees[i] == 1
}
h_vertices = frozenset(h_vertices_from_edges | h_vertices_from_leaves)
h_edges = frozenset(
    frozenset((p, q))
    for p in h_vertices
    for q in h_vertices
    if p != q and p.intersection(q)
)

assert h_vertices == frozenset()
assert h_edges == frozenset()

four_vertex_sets = (
    subset
    for subset in (frozenset((a, b, c, d))
                   for a in h_vertices
                   for b in h_vertices
                   for c in h_vertices
                   for d in h_vertices)
    if len(subset) == 4
)
assert all(
    sum(1 for edge in h_edges if edge.issubset(subset)) != 5
    for subset in four_vertex_sets
)

block_vertices = frozenset()
assert not h_edges
assert block_vertices == frozenset()

c_sets = {
    i: frozenset(p for p in h_vertices if i in p)
    for i in g_vertices
}
assert c_sets[1] == frozenset()
assert c_sets[2] == frozenset()
assert c_sets[1] == c_sets[2]
assert c_sets[1] not in block_vertices
assert c_sets[2] not in block_vertices
assert len(block_vertices) != len(g_vertices)

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
