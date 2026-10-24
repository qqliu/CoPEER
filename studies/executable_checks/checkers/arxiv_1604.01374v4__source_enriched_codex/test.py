r"""All graphs are finite, undirected, and simple. A graph is triangle-free if it has no three distinct pairwise adjacent vertices. Let G have vertex set V(G)={v_1,...,v_n}, where n=|V(G)|>=2, and suppose G is triangle-free. Write deg_G(v_i) for the degree of v_i, and let 0 be a symbol distinct from 1,...,n. Construct H with
V(H)={{i,j}: i,j in {1,...,n}, v_i v_j in E(G), and deg_G(v_i)>1} union {{0,i}: i in {1,...,n} and deg_G(v_i)=1},
where two distinct vertices p,q of H are adjacent exactly when p intersect q is nonempty.

Let K_4^- denote the graph on four vertices with five edges. For a K_4^--free graph X and e,e' in E(X), define e~e' when the endpoints of e and e' together span a clique in X. This is an equivalence relation. For e in E(X), let C_X(e) be the clique consisting of all endpoints of edges in the equivalence class of e. Define B(X) to be the graph whose vertices are the distinct cliques C_X(e), e in E(X), with two distinct such cliques adjacent exactly when their intersection is nonempty.

For each i in {1,...,n}, put C_i={p in V(H): i in p}. The claim is that H is K_4^--free; every C_i is one of the vertices C_H(e) of B(H); the C_i are pairwise distinct and exhaust V(B(H)); and the map phi:V(G)->V(B(H)) given by phi(v_i)=C_i is a graph isomorphism. Equivalently, in addition to being a bijection, it satisfies v_i v_j in E(G) if and only if C_i and C_j are adjacent in B(H), for every distinct i,j."""

import json
from itertools import combinations

RECORD_ID = "arxiv_1604.01374v4__source_enriched_codex"
WITNESS = "On the labeled vertex set {v_1,v_2}, take G with E(G)=∅. It is finite, undirected, simple, and triangle-free. Both degrees are 0; the construction gives V(H)=∅ and E(H)=∅, hence V(B(H))=∅, while C_1=C_2=∅."
REFUTATION = "The claim requires each C_i to be a vertex C_H(e) of B(H) and requires the C_i to be pairwise distinct. Here H has no edges, so B(H) has no vertices at all; neither empty C_i is a vertex of B(H), and C_1=C_2. Thus phi cannot be a bijection or an isomorphism."
SEARCH_SPACE = "All 2 finite undirected simple graphs on the fixed labeled vertex set {v_1,v_2}, enumerated by the two masks for the sole possible edge {v_1,v_2}; both graphs are triangle-free, and the full two-mask space was swept in increasing mask order."


def is_triangle_free(n, edges):
    for a, b, c in combinations(range(1, n + 1), 3):
        if ((a, b) in edges and (a, c) in edges and
                (b, c) in edges):
            return False
    return True


def construct_h(n, edges):
    degrees = {i: 0 for i in range(1, n + 1)}
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1

    vertex_set = set()
    for a, b in edges:
        if degrees[a] > 1:
            vertex_set.add((a, b))
        if degrees[b] > 1:
            vertex_set.add((a, b))
    for i in range(1, n + 1):
        if degrees[i] == 1:
            vertex_set.add((0, i))

    vertices = tuple(sorted(vertex_set))
    h_edges = set()
    for a, b in combinations(range(len(vertices)), 2):
        if set(vertices[a]).intersection(vertices[b]):
            h_edges.add((a, b))
    return vertices, frozenset(h_edges)


def is_clique(vertex_indices, edges):
    ordered = tuple(sorted(vertex_indices))
    for a, b in combinations(ordered, 2):
        if (a, b) not in edges:
            return False
    return True


def is_k4_minus_free(vertex_count, edges):
    for four in combinations(range(vertex_count), 4):
        induced_edge_count = 0
        for a, b in combinations(four, 2):
            if (a, b) in edges:
                induced_edge_count += 1
        if induced_edge_count == 5:
            return False
    return True


def block_vertices(h_edges):
    blocks = set()
    ordered_edges = tuple(sorted(h_edges))
    for edge in ordered_edges:
        endpoints = set()
        edge_endpoints = set(edge)
        for other in ordered_edges:
            combined = edge_endpoints.union(other)
            if is_clique(combined, h_edges):
                endpoints.update(other)
        blocks.add(frozenset(endpoints))
    return frozenset(blocks)


def claim_holds(n, g_edges):
    h_vertices, h_edges = construct_h(n, g_edges)
    if not is_k4_minus_free(len(h_vertices), h_edges):
        return False

    blocks = block_vertices(h_edges)
    c_sets = tuple(
        frozenset(index for index, pair in enumerate(h_vertices) if i in pair)
        for i in range(1, n + 1)
    )

    if any(c_set not in blocks for c_set in c_sets):
        return False
    if len(set(c_sets)) != n:
        return False
    if frozenset(c_sets) != blocks:
        return False

    for i, j in combinations(range(n), 2):
        g_adjacent = (i + 1, j + 1) in g_edges
        b_adjacent = c_sets[i] != c_sets[j] and bool(c_sets[i].intersection(c_sets[j]))
        if g_adjacent != b_adjacent:
            return False
    return True


def main():
    n = 2
    possible_edges = tuple(combinations(range(1, n + 1), 2))
    tested = 0
    triangle_free_tested = 0
    first_counterexample = None

    for mask in range(1 << len(possible_edges)):
        tested += 1
        edges = frozenset(
            edge for bit, edge in enumerate(possible_edges)
            if mask & (1 << bit)
        )
        if not is_triangle_free(n, edges):
            continue
        triangle_free_tested += 1
        if not claim_holds(n, edges) and first_counterexample is None:
            first_counterexample = edges

    assert tested == 2
    assert triangle_free_tested == 2
    assert first_counterexample == frozenset()

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS,
        "refutation_explanation": REFUTATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
