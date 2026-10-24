r"""After adding f_j to T, removing an arbitrary e_i from P keeps the resulting graph connected and destroys its unique circuit."""

import json
from itertools import combinations

RECORD_ID = "reddit_askmath_1togddn"
VERDICT = "CONFIRMED"
NOTES = ("The concrete witness is valid: removing (2,3) after adding (0,2) "
         "isolates vertex 3 while preserving the sole circuit on edges (0,1), "
         "(1,2), and (0,2). This refutes the arbitrary-edge assertion and is a "
         "substantive logical error, not plainly a typo.")


def normalized_edge(left, right):
    if left < right:
        return (left, right)
    return (right, left)


def edges_of_path(sequence):
    result = set()
    index = 0
    while index + 1 < len(sequence):
        result.add(normalized_edge(sequence[index], sequence[index + 1]))
        index += 1
    return result


def reachable(vertices, edges, start):
    found = {start}
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for left, right in edges:
            neighbor = None
            if left == current:
                neighbor = right
            elif right == current:
                neighbor = left
            if neighbor is not None and neighbor not in found:
                found.add(neighbor)
                frontier.append(neighbor)
    return found == set(vertices)


def is_simple_circuit(edge_subset):
    if len(edge_subset) < 3:
        return False
    incident = set()
    degrees = {}
    for left, right in edge_subset:
        incident.add(left)
        incident.add(right)
        degrees[left] = degrees.get(left, 0) + 1
        degrees[right] = degrees.get(right, 0) + 1
    for vertex in incident:
        if degrees[vertex] != 2:
            return False
    start = min(incident)
    return reachable(tuple(sorted(incident)), edge_subset, start)


def circuits(edges):
    ordered = tuple(sorted(edges))
    result = []
    size = 3
    while size <= len(ordered):
        for chosen in combinations(ordered, size):
            candidate = set(chosen)
            if is_simple_circuit(candidate):
                result.append(frozenset(candidate))
        size += 1
    return tuple(result)


def main():
    vertices = (0, 1, 2, 3)
    tree = {
        normalized_edge(0, 1),
        normalized_edge(1, 2),
        normalized_edge(2, 3),
    }
    path_p = (0, 1, 2, 3)
    path_p_prime = (0, 2, 1, 3)
    added = normalized_edge(0, 2)
    removed = normalized_edge(2, 3)

    p_edges = edges_of_path(path_p)
    p_prime_edges = edges_of_path(path_p_prime)
    augmented = set(tree)
    augmented.add(added)
    resulting = set(augmented)
    resulting.remove(removed)

    expected_circuit = frozenset({
        normalized_edge(0, 1),
        normalized_edge(1, 2),
        normalized_edge(0, 2),
    })
    augmented_circuits = circuits(augmented)
    resulting_circuits = circuits(resulting)

    witness_valid = (
        len(set(path_p)) == len(path_p)
        and len(set(path_p_prime)) == len(path_p_prime)
        and path_p[0] == path_p_prime[0]
        and path_p[-1] == path_p_prime[-1]
        and p_edges.issubset(tree)
        and reachable(vertices, tree, vertices[0])
        and len(circuits(tree)) == 0
        and len(tree) == len(vertices) - 1
        and added in p_prime_edges
        and added not in tree
        and removed in p_edges
        and len(augmented_circuits) == 1
        and augmented_circuits[0] == expected_circuit
        and not reachable(vertices, resulting, vertices[0])
        and len(resulting_circuits) == 1
        and resulting_circuits[0] == expected_circuit
    )

    if not witness_valid:
        raise RuntimeError("independent exact verification failed")

    output = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(output, separators=(",", ":")))


if __name__ == "__main__":
    main()
