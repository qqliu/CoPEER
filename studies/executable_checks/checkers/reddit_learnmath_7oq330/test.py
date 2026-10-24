"""Re-adding the removed vertex u preserves, for the same vertex supplied by the inductive hypothesis in G', reachability from every vertex by a directed path of length at most 2."""

import json


def reaches_within_two(edges, start, target):
    frontier = {start}
    for _length in range(3):
        if target in frontier:
            return True
        frontier = {
            destination
            for source, destination in edges
            if source in frontier
        }
    return False


def has_property(vertices, edges, target):
    return all(reaches_within_two(edges, vertex, target) for vertex in vertices)


def main():
    u = "u"
    v = "v"
    vertices = (u, v)
    target = v
    candidates = (
        ((v, u),),
        ((u, v),),
    )

    counterexample_indices = []
    for index, edges in enumerate(candidates):
        reduced_vertices = tuple(vertex for vertex in vertices if vertex != u)
        reduced_edges = tuple(
            edge for edge in edges if u not in edge
        )
        premise = has_property(reduced_vertices, reduced_edges, target)
        conclusion = has_property(vertices, edges, target)
        if premise and not conclusion:
            counterexample_indices.append(index)

    if counterexample_indices != [0]:
        raise AssertionError("unexpected exhaustive-search result")

    result = {
        "record_id": "reddit_learnmath_7oq330",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Let G have vertices {u, v} and the single directed edge v→u. Removing u leaves G' with the sole vertex v, and the supplied vertex is v.",
        "refutation_explanation": "In G', v reaches itself by the length-0 directed path, so every vertex of G' reaches v within 2 steps. After u is re-added, u has no outgoing edge, so no directed path from u to v exists. Thus the same vertex v no longer has the claimed reachability property.",
        "search_space": "Both loop-free directed graphs on the labeled vertices {u, v} having exactly one edge between the two vertices: edge v→u and edge u→v. The program checks both in that fixed order."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
