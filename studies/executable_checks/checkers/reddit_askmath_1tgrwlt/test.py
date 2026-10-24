"""In a circuit-free graph, every walk between two vertices is a path."""

import itertools
import json

RECORD_ID = "reddit_askmath_1tgrwlt"
WITNESS_DESCRIPTION = (
    "The simple undirected graph V={0,1}, E={{0,1}} with the walk "
    "(0,1,0,1) from 0 to 1."
)
REFUTATION_EXPLANATION = (
    "This graph is circuit-free (a simple graph on two vertices has no cycle). "
    "The sequence is a walk because each consecutive pair uses {0,1}, but it "
    "repeats both vertices and repeats the edge {0,1}; by the quoted path "
    "condition it is not a path."
)
SEARCH_SPACE = (
    "All 2 simple undirected graphs on the labeled vertex set {0,1}; for each "
    "graph, all 30 vertex sequences of lengths 1 through 4 (walk lengths 0 "
    "through 3), in mask/length/lexicographic order, for 60 graph-sequence "
    "pairs total. The program tests acyclicity, distinct endpoints, walk "
    "adjacency, and repeated vertices/edges, and sweeps the entire space."
)

VERTICES = (0, 1)
POSSIBLE_EDGES = ((0, 1),)


def canonical_edge(a, b):
    return (a, b) if a < b else (b, a)


def has_cycle(vertices, edges):
    adjacency = {vertex: [] for vertex in vertices}
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    for vertex in vertices:
        adjacency[vertex].sort()

    seen = set()

    def visit(vertex, parent):
        seen.add(vertex)
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                if visit(neighbor, vertex):
                    return True
            elif neighbor != parent:
                return True
        return False

    for vertex in vertices:
        if vertex not in seen and visit(vertex, None):
            return True
    return False


def is_walk(sequence, edges):
    return all(
        canonical_edge(sequence[index], sequence[index + 1]) in edges
        for index in range(len(sequence) - 1)
    )


def main():
    witnesses = []
    examined = 0

    for mask in range(1 << len(POSSIBLE_EDGES)):
        edges = frozenset(
            edge
            for index, edge in enumerate(POSSIBLE_EDGES)
            if mask & (1 << index)
        )
        circuit_free = not has_cycle(VERTICES, edges)

        for sequence_length in range(1, 5):
            for sequence in itertools.product(VERTICES, repeat=sequence_length):
                examined += 1
                if not circuit_free:
                    continue
                if sequence[0] == sequence[-1]:
                    continue
                if not is_walk(sequence, edges):
                    continue

                traversed_edges = tuple(
                    canonical_edge(sequence[index], sequence[index + 1])
                    for index in range(len(sequence) - 1)
                )
                repeats_vertex = len(set(sequence)) != len(sequence)
                repeats_edge = len(set(traversed_edges)) != len(traversed_edges)
                if repeats_vertex or repeats_edge:
                    witnesses.append((mask, sequence))

    if examined != 60 or not witnesses or witnesses[0] != (1, (0, 1, 0, 1)):
        raise RuntimeError("exhaustive search did not produce the expected witness")

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
