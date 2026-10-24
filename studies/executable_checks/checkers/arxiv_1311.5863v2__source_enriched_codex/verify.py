r"""Every chordal graph can be obtained via clique pasting from two chordal graphs whose vertex sets are both proper subsets of its vertex set."""

import json
from itertools import combinations, permutations

RECORD_ID = "arxiv_1311.5863v2__source_enriched_codex"
EXPECTED_VERDICT = "CONFIRMED"
EXPECTED_NOTES = "Exact exhaustive recomputation confirms the witness: K2 is chordal, while two proper vertex subsets covering its vertices must be {0} and {1}; graphs on those sets have no edges and cannot produce K2's edge by clique pasting. The refuted statement is substantive, not plainly a typo: it omits a base-case or indecomposability qualification for complete graphs."


def edge(u, v):
    if u < v:
        return (u, v)
    return (v, u)


def is_clique(vertices, edges):
    for u, v in combinations(sorted(vertices), 2):
        if edge(u, v) not in edges:
            return False
    return True


def is_chordal(vertices, edges):
    ordered_vertices = tuple(sorted(vertices))
    for ordering in permutations(ordered_vertices):
        position = {vertex: index for index, vertex in enumerate(ordering)}
        valid = True
        for vertex in ordering:
            later_neighbors = frozenset(
                other
                for other in ordered_vertices
                if position[other] > position[vertex]
                and edge(vertex, other) in edges
            )
            if not is_clique(later_neighbors, edges):
                valid = False
                break
        if valid:
            return True
    return False


def subsets(vertices):
    ordered = tuple(sorted(vertices))
    result = []
    for mask in range(1 << len(ordered)):
        result.append(
            frozenset(
                ordered[index]
                for index in range(len(ordered))
                if mask & (1 << index)
            )
        )
    return tuple(result)


def all_simple_graphs(vertices):
    possible = tuple(combinations(sorted(vertices), 2))
    graphs = []
    for mask in range(1 << len(possible)):
        graphs.append(
            frozenset(
                possible[index]
                for index in range(len(possible))
                if mask & (1 << index)
            )
        )
    return tuple(graphs)


def can_be_pasted(target_vertices, target_edges):
    proper = tuple(
        part for part in subsets(target_vertices) if part != target_vertices
    )
    for left_vertices in proper:
        for right_vertices in proper:
            if left_vertices | right_vertices != target_vertices:
                continue
            overlap = left_vertices & right_vertices
            for left_edges in all_simple_graphs(left_vertices):
                if not is_chordal(left_vertices, left_edges):
                    continue
                if not is_clique(overlap, left_edges):
                    continue
                for right_edges in all_simple_graphs(right_vertices):
                    if not is_chordal(right_vertices, right_edges):
                        continue
                    if not is_clique(overlap, right_edges):
                        continue
                    if left_edges | right_edges == target_edges:
                        return True
    return False


def main():
    vertices = frozenset((0, 1))
    edges = frozenset(((0, 1),))
    verified = is_chordal(vertices, edges) and not can_be_pasted(vertices, edges)
    verdict = EXPECTED_VERDICT if verified else "REFUTED_WITNESS_INVALID"
    notes = EXPECTED_NOTES if verified else "Independent exact recomputation did not validate the reported witness; the statement therefore remains unresolved by this witness."
    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
