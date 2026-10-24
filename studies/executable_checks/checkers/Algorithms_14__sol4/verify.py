#!/usr/bin/env python3
"""By the time we reach x, the neighbor y is already visited, so the DFS will not take the edge {x, y} as a tree edge"""

import json

RECORD_ID = "Algorithms_14__sol4"
EXPECTED_NOTES = (
    "Exact recomputation gives disc[0]=0, disc[1]=1 and tree edge {0,1}, "
    "but that edge is taken before x=1 is reached, precisely to discover x; "
    "after reaching x, DFS examines {1,0} and does not take it. The report "
    "replaces the stated prospective “will not take” predicate with the "
    "different global predicate “is not a tree edge.” This is a substantive "
    "semantic mismatch, not plainly a typo."
)


def normalized_edge(a, b):
    return (a, b) if a < b else (b, a)


def recompute():
    adjacency = ((1,), (0,))
    discovery = [None, None]
    tree_edges = []
    events = []

    def visit(vertex):
        discovery[vertex] = sum(value is not None for value in discovery)
        events.append(("reach", vertex, vertex))
        for neighbor in adjacency[vertex]:
            edge = normalized_edge(vertex, neighbor)
            events.append(("examine", vertex, neighbor))
            if discovery[neighbor] is None:
                events.append(("take", edge[0], edge[1]))
                tree_edges.append(edge)
                visit(neighbor)
            else:
                events.append(("skip", vertex, neighbor))

    visit(0)

    x = 1
    y = 0
    edge = normalized_edge(x, y)
    reach_x = next(
        index for index, event in enumerate(events)
        if event == ("reach", x, x)
    )
    take_positions = [
        index for index, event in enumerate(events)
        if event == ("take", edge[0], edge[1])
    ]

    premise = discovery[y] < discovery[x]
    globally_tree = edge in tree_edges
    taken_before_reaching_x = any(index < reach_x for index in take_positions)
    taken_after_reaching_x = any(index > reach_x for index in take_positions)
    skipped_when_examined_from_x = ("skip", x, y) in events

    valid_recomputation = (
        discovery == [0, 1]
        and tree_edges == [(0, 1)]
        and premise
        and globally_tree
        and taken_before_reaching_x
        and not taken_after_reaching_x
        and skipped_when_examined_from_x
    )

    if valid_recomputation:
        return "REFUTED_WITNESS_INVALID", EXPECTED_NOTES

    return (
        "CANNOT_REPRODUCE",
        "The reported two-vertex DFS event sequence could not be independently reproduced."
    )


def main():
    verdict, notes = recompute()
    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
