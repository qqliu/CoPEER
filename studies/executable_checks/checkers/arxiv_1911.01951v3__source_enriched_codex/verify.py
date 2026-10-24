r"""Let G=(V,E) be a finite graph of order n. For a vertex x, let N(x) be its open neighborhood and N[x]=N(x)∪{x}. Let v_1,…,v_n be a degeneracy ordering of V: if k is the degeneracy of G, then |N(v_i)∩V_i|≤k for every i∈[n], where [n]={1,…,n} and V_i={v_i,v_{i+1},…,v_n}. For each i∈[n], let G_i be the subgraph of G induced by N[v_i]∩V_i.

Run BronKerboschDeg on this ordering as specified in the source: for each i∈[n], initialize P=N(v_i)∩{v_{i+1},…,v_n}, X=N(v_i)∪{v_1,…,v_{i-1}}, and R={v_i}, and call BronKerboschPivot(P,R,X). In each BronKerboschPivot call with P nonempty, choose an arbitrary pivot u∈P; for every v∈P\N(u), recursively call BronKerboschPivot(P∩N(v),R∪{v},X∩N(v)), then replace P by P\{v} and X by X∪{v}. When P is empty, the call terminates; it reports R precisely when P∪X is empty.

The call tree has the BronKerboschDeg call as its root. Its subtree S_i is rooted at the call BronKerboschPivot(P,{v_i},X) made for v_i. A leaf is a final recursive call, and its associated R_l is the value of R supplied to that call. Let D be the set of leaves at which R is not reported as a maximal clique. Then, for every permitted execution, every i∈[n], and every leaf l∈D lying in S_i, R_l is a maximal clique of G_i: its vertices are pairwise adjacent in G_i, and no clique of G_i strictly contains R_l."""

import json

REPORT = {
    "record_id": "arxiv_1911.01951v3__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic confirms the stated five-vertex execution and its non-reporting leaf R={x,w}, P=∅, X={a,v}; {x,v,w} is a strictly larger clique in G_2. The refutation is substantive, not merely the X-union typo: the same violating leaf occurs with the usual intersection initialization.",
}


def verify():
    vertex_count = 5
    edge_pairs = frozenset((
        (0, 1), (0, 3), (0, 4), (1, 2),
        (1, 3), (1, 4), (3, 4),
    ))
    neighbors = [set() for unused in range(vertex_count)]
    for left, right in edge_pairs:
        assert 0 <= left < right < vertex_count
        neighbors[left].add(right)
        neighbors[right].add(left)

    for vertex in range(vertex_count):
        assert vertex not in neighbors[vertex]
        for other in neighbors[vertex]:
            assert vertex in neighbors[other]

    degeneracy = 0
    for membership in range(1, 1 << vertex_count):
        vertices = tuple(
            vertex for vertex in range(vertex_count)
            if membership & (1 << vertex)
        )
        least_degree = vertex_count
        for vertex in vertices:
            induced_degree = sum(
                1 for other in neighbors[vertex]
                if membership & (1 << other)
            )
            if induced_degree < least_degree:
                least_degree = induced_degree
        if least_degree > degeneracy:
            degeneracy = least_degree

    assert degeneracy == 3
    later_degrees = tuple(
        sum(1 for other in neighbors[vertex] if other >= vertex)
        for vertex in range(vertex_count)
    )
    assert later_degrees == (3, 3, 0, 1, 0)
    assert all(degree <= degeneracy for degree in later_degrees)

    anchor = 1
    initial_p = set(
        other for other in neighbors[anchor] if other > anchor
    )
    stated_x = set(neighbors[anchor]) | set(range(anchor))
    assert initial_p == {2, 3, 4}
    assert stated_x == {0, 2, 3, 4}
    pivot = min(initial_p)
    assert pivot == 2
    assert tuple(sorted(initial_p - neighbors[pivot])) == (2, 3, 4)

    def execute(start_x):
        leaves = []

        def descend(p, r, x, path):
            if not p:
                leaves.append((
                    path, frozenset(r), frozenset(p), frozenset(x)
                ))
                return
            chosen_pivot = min(p)
            scheduled = tuple(sorted(p - neighbors[chosen_pivot]))
            for chosen_vertex in scheduled:
                descend(
                    p & neighbors[chosen_vertex],
                    r | {chosen_vertex},
                    x & neighbors[chosen_vertex],
                    path + (chosen_vertex,),
                )
                p.remove(chosen_vertex)
                x.add(chosen_vertex)

        descend(set(initial_p), {anchor}, set(start_x), ())
        return tuple(leaves)

    witness_leaf = (
        (4,),
        frozenset((1, 4)),
        frozenset(),
        frozenset((0, 3)),
    )
    stated_leaves = execute(stated_x)
    assert witness_leaf in stated_leaves
    assert not witness_leaf[2]
    assert witness_leaf[3]

    gi_vertices = (
        (set(neighbors[anchor]) | {anchor})
        & set(range(anchor, vertex_count))
    )
    assert gi_vertices == {1, 2, 3, 4}

    def is_clique(vertices):
        ordered = tuple(sorted(vertices))
        for first_index in range(len(ordered)):
            for second_index in range(first_index + 1, len(ordered)):
                if ordered[second_index] not in neighbors[ordered[first_index]]:
                    return False
        return True

    leaf_r = set(witness_leaf[1])
    strict_extension = leaf_r | {3}
    assert leaf_r < strict_extension <= gi_vertices
    assert is_clique(leaf_r)
    assert is_clique(strict_extension)

    corrected_x = set(neighbors[anchor]) & set(range(anchor))
    assert corrected_x == {0}
    corrected_leaves = execute(corrected_x)
    assert witness_leaf in corrected_leaves


if __name__ == "__main__":
    verify()
    print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
