r'''Hence, in $\bar{G}$, each vertex is adjacent to all the vertices in the other set, and will not be adjacent to any vertex in the same set as it. in other words, $\bar{G}$ is a complete bipartite graph'''

import json

RECORD_ID = "SE_math_4066749__q"
NO_WITNESS = "No witness was found in the bounded search."
EXPLANATION = (
    "Every graph satisfying the quoted cross-set and same-set adjacency "
    "conditions was exactly the complete bipartite graph on that partition. "
    "This exhausts only the stated finite search space and does not establish "
    "an unbounded claim."
)
SEARCH_SPACE = (
    "All 2,063,284 pairs consisting of a labeled simple undirected graph on n "
    "vertices and an ordered nonempty two-set partition, for each n from 2 "
    "through 6 inclusive."
)


def main():
    examined = 0
    witness = None

    for n in range(2, 7):
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        graph_count = 1 << len(edges)
        all_vertices_mask = (1 << n) - 1

        for partition_mask in range(1, all_vertices_mask):
            expected_mask = 0
            for edge_index, (i, j) in enumerate(edges):
                i_set = (partition_mask >> i) & 1
                j_set = (partition_mask >> j) & 1
                if i_set != j_set:
                    expected_mask |= 1 << edge_index

            for graph_mask in range(graph_count):
                examined += 1

                quoted_conditions_hold = True
                for edge_index, (i, j) in enumerate(edges):
                    adjacent = ((graph_mask >> edge_index) & 1) == 1
                    in_other_sets = (
                        ((partition_mask >> i) & 1)
                        != ((partition_mask >> j) & 1)
                    )
                    if adjacent != in_other_sets:
                        quoted_conditions_hold = False
                        break

                is_complete_bipartite = graph_mask == expected_mask
                if quoted_conditions_hold and not is_complete_bipartite:
                    witness = (n, partition_mask, graph_mask)
                    break

            if witness is not None:
                break
        if witness is not None:
            break

    if witness is not None:
        n, partition_mask, graph_mask = witness
        result = {
            "record_id": RECORD_ID,
            "outcome": "WITNESS_FOUND",
            "witness_description": (
                "n=%d, partition_mask=%d, graph_mask=%d"
                % (n, partition_mask, graph_mask)
            ),
            "refutation_explanation": (
                "The quoted adjacency conditions hold, but the graph edge set "
                "differs from the complete bipartite edge set for the partition."
            ),
            "search_space": SEARCH_SPACE,
        }
    else:
        assert examined == 2063284
        result = {
            "record_id": RECORD_ID,
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": NO_WITNESS,
            "refutation_explanation": EXPLANATION,
            "search_space": SEARCH_SPACE,
        }

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
