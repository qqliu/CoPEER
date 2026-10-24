"""For a graph G on n vertices whose maximum independent-set size is k, the strictly upper-triangular part UA of its adjacency matrix satisfies (UA)^(n-k+1)=θ, and conversely."""

import itertools
import json


def maximum_independent_set_size(n, edges):
    best = 0
    for vertex_mask in range(1 << n):
        independent = True
        for u, v in edges:
            if ((vertex_mask >> u) & 1) and ((vertex_mask >> v) & 1):
                independent = False
                break
        if independent:
            size = sum((vertex_mask >> v) & 1 for v in range(n))
            if size > best:
                best = size
    return best


def multiply(left, right):
    n = len(left)
    return [
        [sum(left[i][t] * right[t][j] for t in range(n)) for j in range(n)]
        for i in range(n)
    ]


def matrix_power(matrix, exponent):
    n = len(matrix)
    result = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for _ in range(exponent):
        result = multiply(result, matrix)
    return result


def is_zero(matrix):
    return all(entry == 0 for row in matrix for entry in row)


def main():
    first_violation = None
    graphs_checked = 0

    for n in range(1, 5):
        pairs = tuple(itertools.combinations(range(n), 2))
        for edge_mask in range(1 << len(pairs)):
            graphs_checked += 1
            edges = tuple(
                pair for index, pair in enumerate(pairs)
                if (edge_mask >> index) & 1
            )
            k = maximum_independent_set_size(n, edges)
            upper = [[0 for _ in range(n)] for _ in range(n)]
            for u, v in edges:
                upper[u][v] = 1
            exponent = n - k + 1
            powered = matrix_power(upper, exponent)
            if not is_zero(powered) and first_violation is None:
                first_violation = (n, edge_mask, edges, k, exponent, powered)

    expected_edges = ((0, 1), (1, 2))
    if graphs_checked != 75:
        raise RuntimeError("bounded search was not completed")
    if first_violation is None:
        raise RuntimeError("expected counterexample was not found")
    n, edge_mask, edges, k, exponent, powered = first_violation
    if not (
        n == 3
        and edge_mask == 5
        and edges == expected_edges
        and k == 2
        and exponent == 2
        and powered[0][2] == 1
    ):
        raise RuntimeError("unexpected first counterexample")

    output = {
        "record_id": "arxiv_0709.2689v3__source_enriched_codex",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The labeled graph on vertices {0,1,2} with edges {(0,1),(1,2)} has maximum independent-set size k=2, but (UA)^(3-2+1)=(UA)^2 is nonzero.",
        "refutation_explanation": "Vertices {0,2} form an independent set, while all three vertices do not, so k=2. With the vertex order 0<1<2, UA has entries UA[0,1]=UA[1,2]=1. Therefore (UA)^2[0,2]=UA[0,1]·UA[1,2]=1, so (UA)^2 is not θ, contradicting the claimed implication.",
        "search_space": "Exhaustively swept all 75 labeled simple undirected graphs on vertex sets {0,...,n-1} for n=1,2,3,4: every edge mask in ascending order over lexicographically ordered vertex pairs. For every graph, the maximum independent-set size was computed by checking all 2^n vertex subsets, and (UA)^(n-k+1) was computed by exact integer matrix multiplication. The stated witness is the first violation in this fixed order."
    }
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
