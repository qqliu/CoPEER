r"""Let G=(V,E) be a finite graph of order n. For a vertex x, let N(x) be its open neighborhood and N[x]=N(x)∪{x}. Let v_1,…,v_n be a degeneracy ordering of V: if k is the degeneracy of G, then |N(v_i)∩V_i|≤k for every i∈[n], where [n]={1,…,n} and V_i={v_i,v_{i+1},…,v_n}. For each i∈[n], let G_i be the subgraph of G induced by N[v_i]∩V_i.

Run BronKerboschDeg on this ordering as specified in the source: for each i∈[n], initialize P=N(v_i)∩{v_{i+1},…,v_n}, X=N(v_i)∪{v_1,…,v_{i-1}}, and R={v_i}, and call BronKerboschPivot(P,R,X). In each BronKerboschPivot call with P nonempty, choose an arbitrary pivot u∈P; for every v∈P\N(u), recursively call BronKerboschPivot(P∩N(v),R∪{v},X∩N(v)), then replace P by P\{v} and X by X∪{v}. When P is empty, the call terminates; it reports R precisely when P∪X is empty.

The call tree has the BronKerboschDeg call as its root. Its subtree S_i is rooted at the call BronKerboschPivot(P,{v_i},X) made for v_i. A leaf is a final recursive call, and its associated R_l is the value of R supplied to that call. Let D be the set of leaves at which R is not reported as a maximal clique. Then, for every permitted execution, every i∈[n], and every leaf l∈D lying in S_i, R_l is a maximal clique of G_i: its vertices are pairwise adjacent in G_i, and no clique of G_i strictly contains R_l."""

import json
from itertools import combinations, permutations

RECORD_ID = "arxiv_1911.01951v3__source_enriched_codex"
WITNESS_DESCRIPTION = "Vertices (a,x,u,v,w)=(0,1,2,3,4) are ordered a,x,u,v,w. Edges are ax,av,aw,xu,xv,xw,vw. The degeneracy is 3. In S_2 choose pivot u and process P\\N(u) in the order u,v,w; the branch for w reaches the leaf R={x,w}, P=∅, X={a,v}."
REFUTATION_EXPLANATION = "The leaf is in D because P is empty and X is nonempty, so R is not reported. But v belongs to V(G_2), is adjacent to both x and w, and therefore {x,v,w} is a clique of G_2 strictly containing R={x,w}; hence R is not maximal in G_2."
SEARCH_SPACE = "All simple undirected graphs on n=1,...,5 vertices with the fixed order 0<...<n-1 whose fixed order satisfies the stated degeneracy bound; for every i, all reachable BronKerboschPivot call states arising from every pivot choice and every permutation of each snapshot P\\N(u) were swept. Relabeling makes this fixed-order enumeration cover every ordered graph of these sizes."

NAMED_EDGES = frozenset({
    (0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (3, 4)
})


def make_adjacency(n, edge_mask, pairs):
    adjacency = [set() for _ in range(n)]
    for bit, edge in enumerate(pairs):
        if edge_mask & (1 << bit):
            a, b = edge
            adjacency[a].add(b)
            adjacency[b].add(a)
    return tuple(frozenset(neighbors) for neighbors in adjacency)


def graph_degeneracy(adjacency):
    n = len(adjacency)
    answer = 0
    for subset in range(1, 1 << n):
        vertices = tuple(v for v in range(n) if subset & (1 << v))
        minimum_degree = min(
            sum(1 for w in adjacency[v] if subset & (1 << w))
            for v in vertices
        )
        if minimum_degree > answer:
            answer = minimum_degree
    return answer


def fixed_order_is_degeneracy_order(adjacency, k):
    n = len(adjacency)
    for i in range(n):
        later_degree = sum(1 for v in adjacency[i] if v >= i)
        if later_degree > k:
            return False
    return True


def clique_failure_or_extension(adjacency, gi_vertices, result):
    ordered_result = tuple(sorted(result))
    for a, b in combinations(ordered_result, 2):
        if b not in adjacency[a]:
            return ("nonclique", (a, b))
    for candidate in sorted(gi_vertices - result):
        if all(candidate in adjacency[v] for v in result):
            return ("extension", candidate)
    return None


def named_mask(pairs):
    mask = 0
    for bit, edge in enumerate(pairs):
        if edge in NAMED_EDGES:
            mask |= 1 << bit
    return mask


def verify_named_execution():
    n = 5
    pairs = tuple(combinations(range(n), 2))
    mask = named_mask(pairs)
    adjacency = make_adjacency(n, mask, pairs)
    k = graph_degeneracy(adjacency)
    if k != 3 or not fixed_order_is_degeneracy_order(adjacency, k):
        return False

    i = 1
    p = set(adjacency[i]) & set(range(i + 1, n))
    x = set(adjacency[i]) | set(range(i))
    if p != {2, 3, 4} or x != {0, 2, 3, 4}:
        return False
    if p - set(adjacency[2]) != {2, 3, 4}:
        return False

    current_p = set(p)
    current_x = set(x)
    for vertex in (2, 3):
        current_p.remove(vertex)
        current_x.add(vertex)

    vertex = 4
    leaf_p = current_p & set(adjacency[vertex])
    leaf_r = {i, vertex}
    leaf_x = current_x & set(adjacency[vertex])
    gi_vertices = {i} | (set(adjacency[i]) & set(range(i, n)))
    failure = clique_failure_or_extension(adjacency, gi_vertices, leaf_r)
    return leaf_p == set() and leaf_x == {0, 3} and failure == ("extension", 3)


def exhaustive_sweep():
    stats = {
        "graphs": 0,
        "states": 0,
        "leaves": 0,
        "violations": 0,
        "named_reached": False,
    }

    for n in range(1, 6):
        pairs = tuple(combinations(range(n), 2))
        selected_mask = named_mask(pairs) if n == 5 else -1
        for edge_mask in range(1 << len(pairs)):
            adjacency = make_adjacency(n, edge_mask, pairs)
            k = graph_degeneracy(adjacency)
            if not fixed_order_is_degeneracy_order(adjacency, k):
                continue
            stats["graphs"] += 1

            for i in range(n):
                initial_p = set(adjacency[i]) & set(range(i + 1, n))
                initial_x = set(adjacency[i]) | set(range(i))
                initial_r = {i}
                gi_vertices = {i} | (set(adjacency[i]) & set(range(i, n)))
                seen = set()

                def explore(p, r, x):
                    key = (
                        tuple(sorted(p)),
                        tuple(sorted(r)),
                        tuple(sorted(x)),
                    )
                    if key in seen:
                        return
                    seen.add(key)
                    stats["states"] += 1

                    if not p:
                        stats["leaves"] += 1
                        if x:
                            failure = clique_failure_or_extension(
                                adjacency, gi_vertices, r
                            )
                            if failure is not None:
                                stats["violations"] += 1
                                if (
                                    n == 5
                                    and edge_mask == selected_mask
                                    and i == 1
                                    and r == {1, 4}
                                    and x == {0, 3}
                                    and failure == ("extension", 3)
                                ):
                                    stats["named_reached"] = True
                        return

                    for pivot in sorted(p):
                        candidates = tuple(sorted(p - set(adjacency[pivot])))
                        for branch_order in permutations(candidates):
                            current_p = set(p)
                            current_x = set(x)
                            for vertex in branch_order:
                                explore(
                                    current_p & set(adjacency[vertex]),
                                    r | {vertex},
                                    current_x & set(adjacency[vertex]),
                                )
                                current_p.remove(vertex)
                                current_x.add(vertex)

                explore(initial_p, initial_r, initial_x)

    return stats


def main():
    if not verify_named_execution():
        raise RuntimeError("the named execution did not verify")
    stats = exhaustive_sweep()
    if stats["violations"] == 0 or not stats["named_reached"]:
        raise RuntimeError("the exhaustive bounded sweep missed the witness")

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
