r"""The displayed definition of $G_1 \sqcap G_2$ yields the set of maximal common subgraphs of two labeled graphs and therefore defines their graph intersection."""

import json

RECORD_ID = "arxiv_1504.05457v2__source_enriched_codex"
NOTES = (
    "Exact recomputation confirms the witness. For the one-vertex edgeless "
    "host, the common subgraphs are the empty graph and the host itself. The "
    "displayed predicate rejects both because its universal quantifier includes "
    "G_* = G and the subgraph relation is reflexive, while the actual "
    "maximal-common-subgraph set contains the host. The refutation is "
    "substantive as written, though the formula is plainly likely to contain "
    "a missing strictness or distinctness typo."
)


def is_subgraph(left, right):
    left_vertices, left_edges = left
    right_vertices, right_edges = right
    return (
        left_vertices.issubset(right_vertices)
        and left_edges.issubset(right_edges)
    )


def main():
    no_vertices = frozenset()
    one_vertex = frozenset((0,))
    no_edges = frozenset()

    empty_graph = (no_vertices, no_edges)
    host_graph = (one_vertex, no_edges)
    candidates = (empty_graph, host_graph)

    common = tuple(
        graph
        for graph in candidates
        if is_subgraph(graph, host_graph) and is_subgraph(graph, host_graph)
    )

    displayed = tuple(
        graph
        for graph in common
        if all(not is_subgraph(graph, other) for other in common)
    )

    genuine_maximal = tuple(
        graph
        for graph in common
        if all(
            other == graph or not is_subgraph(graph, other)
            for other in common
        )
    )

    assert is_subgraph(host_graph, host_graph)
    assert common == (empty_graph, host_graph)
    assert displayed == ()
    assert genuine_maximal == (host_graph,)
    assert displayed != genuine_maximal

    result = {
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED",
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
