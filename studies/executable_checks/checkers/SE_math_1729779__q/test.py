"""Since $H$ is a cycle, $H - e$ is still connected"""

import json


def remains_connected(n, deleted_edge):
    adjacency = [[] for _ in range(n)]
    for edge_index in range(n):
        if edge_index == deleted_edge:
            continue
        left = edge_index
        right = (edge_index + 1) % n
        adjacency[left].append(right)
        adjacency[right].append(left)

    seen = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == n


def main():
    checked = 0
    counterexamples = []
    for n in range(3, 13):
        for deleted_edge in range(n):
            checked += 1
            if not remains_connected(n, deleted_edge):
                counterexamples.append((n, deleted_edge))

    assert checked == 75
    assert counterexamples == []

    result = {
        "record_id": "SE_math_1729779__q",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness is claimed; the quote does not specify whether graphs are directed or undirected, what 'connected' means, or a finite bound on H.",
        "refutation_explanation": "The program finds no failure among canonical finite simple undirected cycles C_n for 3 <= n <= 12, but that interpretation and bound are not supplied by the quote. Therefore the bounded sweep cannot decide the unqualified claim.",
        "search_space": "Exactly 75 pairs (H,e): H is the canonical simple undirected cycle C_n on vertices 0,...,n-1 for each integer n from 3 through 12, and e is each of its n edges in index order 0,...,n-1."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
