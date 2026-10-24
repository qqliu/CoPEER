"""if the graph has $k$ edges, there are at most $k!$ paths that do not use the same edge more than once"""

import json
from itertools import combinations, permutations
from math import factorial

RECORD_ID = "SE_cs_143__a153"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The simple undirected graph on vertices {0,1,2} with edges {0-1,0-2} "
    "has k=2 and three nonempty simple paths up to reversal: 0-1, 0-2, "
    "and 1-0-2."
)
REFUTATION_EXPLANATION = (
    "For this witness, k! = 2. There are three distinct paths even after "
    "identifying each path with its reverse, and every listed path uses each "
    "edge at most once. Since 3 > 2, the claimed upper bound fails."
)
SEARCH_SPACE = (
    "All 12 labeled finite simple undirected graphs on vertex sets "
    "{0,...,n-1} for n=0,1,2,3 (all 2^(n choose 2) edge subsets), with "
    "every nonempty vertex-simple path exhaustively enumerated and paths "
    "identified with their reversals."
)


def enumerate_paths(vertex_count, edges):
    paths = set()
    for path_vertex_count in range(2, vertex_count + 1):
        for sequence in permutations(range(vertex_count), path_vertex_count):
            valid = True
            for index in range(path_vertex_count - 1):
                edge = tuple(sorted((sequence[index], sequence[index + 1])))
                if edge not in edges:
                    valid = False
                    break
            if valid:
                reverse = sequence[::-1]
                paths.add(min(sequence, reverse))
    return paths


def main():
    first_witness = None
    graphs_examined = 0

    for vertex_count in range(4):
        possible_edges = tuple(combinations(range(vertex_count), 2))
        for mask in range(1 << len(possible_edges)):
            edges = frozenset(
                possible_edges[index]
                for index in range(len(possible_edges))
                if mask & (1 << index)
            )
            paths = enumerate_paths(vertex_count, edges)
            edge_count = len(edges)
            graphs_examined += 1
            if len(paths) > factorial(edge_count) and first_witness is None:
                first_witness = (vertex_count, edges, paths)

    assert graphs_examined == 12
    assert first_witness is not None
    vertex_count, edges, paths = first_witness
    assert vertex_count == 3
    assert edges == frozenset(((0, 1), (0, 2)))
    assert paths == {(0, 1), (0, 2), (1, 0, 2)}
    assert len(paths) == 3
    assert factorial(len(edges)) == 2

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
