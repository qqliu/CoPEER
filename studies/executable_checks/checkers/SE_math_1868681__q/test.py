r"""Therefore the formula for the greatest number of edges on a bipartite graph on $p$ edges is $\frac{p^2}{4}$."""

import json
from fractions import Fraction

RECORD_ID = "SE_math_1868681__q"
SEARCH_SPACE = (
    "All integers p from 0 through 16, in increasing order; for each p, "
    "the program checks the explicit bipartite matching with vertices "
    "0,...,2p-1 and edges (2i,2i+1) for 0 <= i < p."
)


def matching(p):
    vertices = tuple(range(2 * p))
    edges = tuple((2 * i, 2 * i + 1) for i in range(p))
    return vertices, edges


def is_bipartite(vertices, edges):
    colors = {}
    adjacency = {vertex: [] for vertex in vertices}
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    for start in vertices:
        if start in colors:
            continue
        colors[start] = 0
        queue = [start]
        position = 0
        while position < len(queue):
            vertex = queue[position]
            position += 1
            for neighbor in adjacency[vertex]:
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[vertex]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[vertex]:
                    return False
    return True


def main():
    witness = None
    for p in range(17):
        vertices, edges = matching(p)
        claimed_greatest = Fraction(p * p, 4)
        actual_edge_count = len(edges)
        if (
            actual_edge_count == p
            and is_bipartite(vertices, edges)
            and Fraction(actual_edge_count, 1) > claimed_greatest
        ):
            witness = p
            break

    if witness == 1:
        result = {
            "record_id": RECORD_ID,
            "outcome": "WITNESS_FOUND",
            "witness_description": (
                "For p=1, take the graph with vertices (0, 1) and the single "
                "edge (0, 1). It is bipartite and has exactly one edge."
            ),
            "refutation_explanation": (
                "The exhibited graph is a bipartite graph on p=1 edge and has "
                "1 edge, whereas the claimed formula gives p^2/4=1/4. Thus "
                "the claimed greatest number is smaller than the edge count "
                "of an admissible graph."
            ),
            "search_space": SEARCH_SPACE,
        }
    else:
        result = {
            "record_id": RECORD_ID,
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No witness was found in the bounded candidate family.",
            "refutation_explanation": "The bounded search found no checked matching above the claimed value.",
            "search_space": SEARCH_SPACE,
        }

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
