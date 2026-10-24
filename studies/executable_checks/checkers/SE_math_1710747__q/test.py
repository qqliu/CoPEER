r"""It suffices to show that $\chi(\partial G)=3$ is order to establish that $G$ is $3-$colourable."""

import json
from itertools import combinations, product


def is_three_colorable(vertex_count, edges):
    for coloring in product(range(3), repeat=vertex_count):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def main():
    graph_count = 0
    non_three_colorable_count = 0

    for vertex_count in range(1, 6):
        possible_edges = tuple(combinations(range(vertex_count), 2))
        for edge_mask in range(1 << len(possible_edges)):
            edges = tuple(
                edge
                for edge_index, edge in enumerate(possible_edges)
                if edge_mask & (1 << edge_index)
            )
            graph_count += 1
            if not is_three_colorable(vertex_count, edges):
                non_three_colorable_count += 1

    assert graph_count == 1099
    assert non_three_colorable_count > 0

    result = {
        "record_id": "SE_math_1710747__q",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be certified because the supplied quote does not define ∂G or specify its relation to G.",
        "refutation_explanation": "The bounded sweep exactly decides 3-colourability of each candidate G, but the antecedent χ(∂G)=3 cannot be evaluated from the supplied data. Thus no candidate can be certified as violating the implication, and the sweep cannot justify an exhaustive negative for the claim.",
        "search_space": "All 1,099 labeled simple undirected graphs G on 1 through 5 vertices, in increasing vertex count and then increasing edge-bitmask order; every one of the 3^n color assignments is checked in lexicographic order when testing 3-colourability. No space of boundaries ∂G can be swept because ∂ is undefined."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
