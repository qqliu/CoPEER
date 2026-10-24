"""Since there aren't any edge the number of vertices must be equal to $1$ or $0$."""

import json


def main():
    vertices = tuple(range(2))
    edges = frozenset()

    valid_edges = True
    for edge in edges:
        if len(edge) != 2:
            valid_edges = False
            break
        left, right = tuple(edge)
        if left == right or left not in vertices or right not in vertices:
            valid_edges = False
            break

    is_valid_graph = len(set(vertices)) == len(vertices) and valid_edges
    contradicts_claim = is_valid_graph and len(edges) == 0 and len(vertices) not in (0, 1)

    if contradicts_claim:
        verdict = "CONFIRMED"
        notes = "The literal statement is substantively false, not plainly a typo: a valid simple undirected graph can have two vertices and an empty edge set."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The reported two-vertex edgeless graph did not validate as a counterexample."

    result = {
        "record_id": "SE_math_782216__q",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
