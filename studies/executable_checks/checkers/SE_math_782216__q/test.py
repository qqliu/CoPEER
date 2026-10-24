"""
Since there aren't any edge the number of vertices must be equal to $1$ or $0$.
"""

import itertools
import json


def main():
    first_witness = None
    examined = 0

    for vertex_count in range(3):
        possible_edges = tuple(itertools.combinations(range(vertex_count), 2))
        for edge_bits in itertools.product((0, 1), repeat=len(possible_edges)):
            edges = tuple(
                edge
                for edge, included in zip(possible_edges, edge_bits)
                if included == 1
            )
            examined += 1
            if not edges and vertex_count not in (0, 1) and first_witness is None:
                first_witness = (vertex_count, edges)

    assert examined == 4
    assert first_witness == (2, ())

    result = {
        "record_id": "SE_math_782216__q",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The labeled graph with vertex set {0, 1} and edge set empty has exactly 2 vertices and no edges.",
        "refutation_explanation": "This graph has no edges, but its number of vertices is 2, which is neither 1 nor 0, so it violates the claim.",
        "search_space": "All 4 labeled loopless simple undirected graphs with vertex set range(n) for n in {0, 1, 2}, obtained by enumerating every subset of unordered vertex pairs in fixed lexicographic order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
