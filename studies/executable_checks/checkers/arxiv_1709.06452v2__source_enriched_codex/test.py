"""The map c(φ)=|⋃_{v∈V(F)}φ(v)| is a proper coloring of the strong compatibility graph of Hom_p(F,K_n)."""

import json
from itertools import product

RECORD_ID = "arxiv_1709.06452v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete Hom_p(F,K_n) witness is certified. The first abstract "
    "ambiguity model has two vertices, no C-edge, one putative strong edge, "
    "and colors (0,0), but the quote does not establish that this model comes "
    "from Hom_p(F,K_n)."
)
REFUTATION_EXPLANATION = (
    "The quote states unequal colors for pairs connected in C and then "
    "concludes properness for \\widetilde C, but it supplies neither definitions "
    "of Hom_p and its vertices nor a definition of strong compatibility "
    "adjacency nor the relation between C and \\widetilde C. Consequently the "
    "bounded relational model can expose the missing bridge but cannot be "
    "promoted to a mathematical counterexample."
)
SEARCH_SPACE = (
    "Exhaustively swept 1,745 abstract labeled interpretations: for each "
    "vertex count n in {1,2,3}, every simple undirected C graph, every "
    "independent simple undirected putative-strong graph, and every coloring "
    "into {0,...,n-1}; totals are 1 + 16 + 1,728 = 1,745. These are logical "
    "test models, not an exhaustive space of Hom_p(F,K_n) instances."
)


def edge_list(vertex_count):
    return tuple(
        (left, right)
        for left in range(vertex_count)
        for right in range(left + 1, vertex_count)
    )


def has_edge(mask, edge_index):
    return (mask & (1 << edge_index)) != 0


def exhaustive_abstract_search():
    tested = 0
    first_ambiguity = None

    for vertex_count in range(1, 4):
        edges = edge_list(vertex_count)
        graph_count = 1 << len(edges)
        for c_mask in range(graph_count):
            for strong_mask in range(graph_count):
                for colors in product(range(vertex_count), repeat=vertex_count):
                    tested += 1
                    quote_condition = all(
                        not has_edge(c_mask, index)
                        or colors[left] != colors[right]
                        for index, (left, right) in enumerate(edges)
                    )
                    strong_condition = all(
                        not has_edge(strong_mask, index)
                        or colors[left] != colors[right]
                        for index, (left, right) in enumerate(edges)
                    )
                    if quote_condition and not strong_condition:
                        candidate = (
                            vertex_count,
                            c_mask,
                            strong_mask,
                            tuple(colors),
                        )
                        if first_ambiguity is None:
                            first_ambiguity = candidate

    return tested, first_ambiguity


def main():
    tested, first_ambiguity = exhaustive_abstract_search()
    assert tested == 1745
    assert first_ambiguity == (2, 0, 1, (0, 0))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
