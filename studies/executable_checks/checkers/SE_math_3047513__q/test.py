"""Color this edge $AB$ red and delete all other edges from $B$ and observe the rest of the graph (without $A$ and $B$ also). This graph is a forest so in each component we can color edges red so that each node has odd red edges (by induction hypothetis). So we are done, just pave all red edges."""

import json
from itertools import combinations

RECORD_ID = "SE_math_3047513__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No claim-valid witness can be named from the quote. The illustrative sweep's first obstruction to the forest-only inference is the one-vertex forest, whose sole vertex has red degree 0, which is even."
REFUTATION_EXPLANATION = "The quote refers to \"this graph,\" an edge AB, and an induction hypothesis without specifying the graph, hypotheses, quantifiers, or what \"pave\" formally requires. The finite sweep proves only that being a forest does not by itself guarantee an odd-red-degree coloring; it cannot establish that the unspecified graph in the claim is the obstructing forest."
SEARCH_SPACE = "Illustrative only (not exhaustive for the supplied referential claim): for each n in {1,2,3,4,5}, every labeled simple undirected graph on vertices {0,...,n-1} was enumerated; every forest was retained, and every subset of its edges was tested as the red set."


def is_forest(vertex_count, edges):
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
    return True


def has_all_odd_red_degrees(vertex_count, edges):
    for red_mask in range(1 << len(edges)):
        degrees = [0] * vertex_count
        for edge_index, (left, right) in enumerate(edges):
            if red_mask & (1 << edge_index):
                degrees[left] += 1
                degrees[right] += 1
        if all(degree % 2 == 1 for degree in degrees):
            return True
    return False


def exhaustive_illustrative_sweep():
    first_obstruction = None
    for vertex_count in range(1, 6):
        possible_edges = tuple(combinations(range(vertex_count), 2))
        for graph_mask in range(1 << len(possible_edges)):
            edges = tuple(
                edge
                for edge_index, edge in enumerate(possible_edges)
                if graph_mask & (1 << edge_index)
            )
            if not is_forest(vertex_count, edges):
                continue
            if not has_all_odd_red_degrees(vertex_count, edges):
                if first_obstruction is None:
                    first_obstruction = (vertex_count, edges)
    return first_obstruction


def main():
    first_obstruction = exhaustive_illustrative_sweep()
    assert first_obstruction == (1, ())
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
