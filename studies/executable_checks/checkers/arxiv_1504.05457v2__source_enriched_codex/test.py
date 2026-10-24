r"""The displayed definition of $G_1 \sqcap G_2$ yields the set of maximal common subgraphs of two labeled graphs and therefore defines their graph intersection."""

import json
from itertools import combinations, product

RECORD_ID = "arxiv_1504.05457v2__source_enriched_codex"
WITNESS = (
    "Let G1 = G2 be the undirected simple labeled graph with the single vertex "
    "labeled 0 and no edges. Its maximal common subgraph is that same one-vertex "
    "graph, but the displayed definition produces the empty set."
)
EXPLANATION = (
    "For any common subgraph G, the universal quantifier permits G_* = G. By "
    "reflexivity of the subgraph relation, G_* >= G then holds, contradicting "
    "the required G_* not >= G. Thus the displayed predicate rejects every "
    "common subgraph, including the maximal graph in the concrete witness."
)
SPACE = (
    "Exhaustive sweep of the sole ordered host pair (G1, G2) in which both hosts "
    "are the undirected simple labeled graph with vertex set {0} and no edges. "
    "Both graphs over the label universe {0}—the empty graph and the one-vertex "
    "graph—were tested as subgraph candidates, with <= implemented by vertex "
    "and edge inclusion."
)


def all_graphs(labels):
    graphs = []
    for vertex_mask in range(1 << len(labels)):
        vertices = frozenset(
            labels[index]
            for index in range(len(labels))
            if vertex_mask & (1 << index)
        )
        possible_edges = tuple(combinations(sorted(vertices), 2))
        for edge_mask in range(1 << len(possible_edges)):
            edges = frozenset(
                possible_edges[index]
                for index in range(len(possible_edges))
                if edge_mask & (1 << index)
            )
            graphs.append((vertices, edges))
    return tuple(graphs)


def leq(left, right):
    return left[0].issubset(right[0]) and left[1].issubset(right[1])


def main():
    graphs = all_graphs((0,))
    hosts = tuple(graph for graph in graphs if graph[0] == frozenset((0,)))
    discrepancies = []

    for g1, g2 in product(hosts, repeat=2):
        common = tuple(g for g in graphs if leq(g, g1) and leq(g, g2))
        displayed = tuple(
            g
            for g in common
            if all(not leq(g, g_star) for g_star in common)
        )
        maximal = tuple(
            g
            for g in common
            if not any(g != g_star and leq(g, g_star) for g_star in common)
        )
        if displayed != maximal:
            discrepancies.append((g1, g2, displayed, maximal))

    expected_host = (frozenset((0,)), frozenset())
    assert len(hosts) == 1
    assert len(discrepancies) == 1
    assert discrepancies[0] == (
        expected_host,
        expected_host,
        (),
        (expected_host,),
    )

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS,
        "refutation_explanation": EXPLANATION,
        "search_space": SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
