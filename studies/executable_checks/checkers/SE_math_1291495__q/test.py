"""$G'$ is a tree with $k-1$ edges and $k+1$ vertices. $G$ has $k-1+m$ edges."""

import itertools
import json

RECORD_ID = "SE_math_1291495__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = ("Take k=1 and let G' be the labeled simple graph on vertices {0,1} "
                       "with the single edge {0,1}. It is connected and acyclic, hence a tree, "
                       "and it has k+1=2 vertices but 1 edge rather than k-1=0 edges.")
REFUTATION_EXPLANATION = ("The first assertion in the target claim is already false: the exhaustive "
                          "search finds the two-vertex tree, whose edge count is 1, while the claimed "
                          "count for k=1 is 0. Therefore the combined claim is violated independently "
                          "of G and m.")
SEARCH_SPACE = ("All 1,098 labeled simple undirected graphs on vertex set {0,...,k}, for every integer "
                "k from 1 through 4: 2 graphs for k=1, 8 for k=2, 64 for k=3, and 1,024 for k=4. "
                "Every graph was checked exactly for connectedness, acyclicity, and whether its edge "
                "count differs from k-1.")


def connected_and_acyclic(vertex_count, edges):
    parent = list(range(vertex_count))

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for left, right in edges:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        parent[right_root] = left_root

    root = find(0)
    return all(find(vertex) == root for vertex in range(vertex_count))


def search():
    first_witness = None
    graphs_checked = 0
    for k in range(1, 5):
        vertex_count = k + 1
        possible_edges = list(itertools.combinations(range(vertex_count), 2))
        for mask in range(1 << len(possible_edges)):
            edges = tuple(
                edge for index, edge in enumerate(possible_edges)
                if mask & (1 << index)
            )
            graphs_checked += 1
            if connected_and_acyclic(vertex_count, edges) and len(edges) != k - 1:
                if first_witness is None:
                    first_witness = (k, edges)
    assert graphs_checked == 1098
    assert first_witness == (1, ((0, 1),))
    return first_witness


def main():
    search()
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
