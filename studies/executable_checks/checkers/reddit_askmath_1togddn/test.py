"""After adding f_j to T, removing an arbitrary e_i from P keeps the resulting graph connected and destroys its unique circuit."""

import json

RECORD_ID = "reddit_askmath_1togddn"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = ("On vertices (0,1,2,3), let T have edges {(0,1),(1,2),(2,3)}, "
                       "let P be the 0-1-2-3 path, let P' be the 0-2-1-3 path, "
                       "choose f_j=(0,2), and remove e_i=(2,3).")
REFUTATION_EXPLANATION = ("T+(0,2) has the unique circuit 0-1-2-0. Removing (2,3), "
                          "which is in P but not in that circuit, leaves vertex 3 "
                          "isolated and leaves the circuit intact; thus the result is "
                          "disconnected and not circuit-free.")
SEARCH_SPACE = ("Exhaustively swept the 6 pairs formed by the 2 edges of P' not in T, "
                "{(0,2),(1,3)}, and the 3 edges of P, "
                "{(0,1),(1,2),(2,3)}, in the fixed four-vertex configuration "
                "described in the witness.")


def edge(a, b):
    return (a, b) if a < b else (b, a)


def path_edges(path):
    return tuple(edge(path[index], path[index + 1])
                 for index in range(len(path) - 1))


def is_connected(vertices, edges):
    adjacency = {vertex: [] for vertex in vertices}
    for a, b in sorted(edges):
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = {vertices[0]}
    pending = [vertices[0]]
    while pending:
        vertex = pending.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == len(vertices)


def is_acyclic(vertices, edges):
    parent = {vertex: vertex for vertex in vertices}

    def find(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for a, b in sorted(edges):
        root_a = find(a)
        root_b = find(b)
        if root_a == root_b:
            return False
        parent[root_b] = root_a
    return True


def main():
    vertices = (0, 1, 2, 3)
    tree = frozenset((edge(0, 1), edge(1, 2), edge(2, 3)))
    path_p = (0, 1, 2, 3)
    path_p_prime = (0, 2, 1, 3)

    assert len(set(path_p)) == len(path_p)
    assert len(set(path_p_prime)) == len(path_p_prime)
    assert path_p[0] == path_p_prime[0]
    assert path_p[-1] == path_p_prime[-1]
    assert set(path_edges(path_p)).issubset(tree)
    assert is_connected(vertices, tree)
    assert is_acyclic(vertices, tree)

    f_choices = tuple(candidate for candidate in path_edges(path_p_prime)
                      if candidate not in tree)
    e_choices = path_edges(path_p)
    violations = []
    swept = 0

    for f_j in f_choices:
        augmented = tree | {f_j}
        assert is_connected(vertices, augmented)
        assert not is_acyclic(vertices, augmented)
        assert len(augmented) == len(vertices)
        for e_i in e_choices:
            swept += 1
            resulting = augmented - {e_i}
            connected = is_connected(vertices, resulting)
            circuit_free = is_acyclic(vertices, resulting)
            if not connected or not circuit_free:
                violations.append((f_j, e_i, connected, circuit_free))

    assert f_choices == ((0, 2), (1, 3))
    assert e_choices == ((0, 1), (1, 2), (2, 3))
    assert swept == 6
    assert violations[0] == ((0, 2), (2, 3), False, False)

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
