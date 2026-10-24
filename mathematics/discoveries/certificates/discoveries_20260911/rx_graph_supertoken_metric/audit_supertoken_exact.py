#!/usr/bin/env python3
"""Independent exact audit of the k=2 supertoken metric certificate.

Run with Python 3. Uses only integer arithmetic and the standard library.
Reads no source files, prior checkers, databases, or network resources.
The finite checks are certificates for the explicitly enumerated instances;
the universal claims additionally require the logical proofs in the audit.
"""

from collections import deque
from itertools import combinations, combinations_with_replacement
import json
from math import comb


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def token_vertex(n, occupied):
    vertex = [0] * n
    for coordinate in occupied:
        vertex[coordinate] += 1
    return tuple(vertex)


def vertices_k2(n):
    return tuple(token_vertex(n, pair)
                 for pair in combinations_with_replacement(range(n), 2))


def support(vertex):
    return tuple(i for i, value in enumerate(vertex) if value > 0)


def exact_distance(left, right):
    twice_distance = sum(abs(a - b) for a, b in zip(left, right))
    require(twice_distance % 2 == 0, "Nonintegral half-L1 distance")
    return twice_distance // 2


def token_move_distances(vertices):
    """Build edges directly by transferring one token, then run BFS."""
    n = len(vertices[0])
    index = {vertex: i for i, vertex in enumerate(vertices)}
    adjacency = [set() for _ in vertices]
    for i, vertex in enumerate(vertices):
        for origin in range(n):
            if vertex[origin] == 0:
                continue
            for destination in range(n):
                if origin == destination:
                    continue
                moved = list(vertex)
                moved[origin] -= 1
                moved[destination] += 1
                adjacency[i].add(index[tuple(moved)])
    for i, neighbors in enumerate(adjacency):
        require(i not in neighbors, "Unexpected self-loop")
        require(all(i in adjacency[j] for j in neighbors), "Asymmetric edge")
    distances = []
    for start in range(len(vertices)):
        row = [-1] * len(vertices)
        row[start] = 0
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if row[neighbor] == -1:
                    row[neighbor] = row[current] + 1
                    queue.append(neighbor)
        require(all(value >= 0 for value in row), "Disconnected token graph")
        distances.append(tuple(row))
    return tuple(distances), sum(map(len, adjacency)) // 2


def local_table(leaf_count):
    center = 0
    leaves = range(1, leaf_count + 1)
    table = {}
    for size in range(3):
        for occupied in combinations(range(leaf_count + 1), size):
            measurement = tuple(int(center in occupied) + int(j in occupied)
                                for j in leaves)
            require(measurement not in table, "Local support collision")
            table[measurement] = occupied
    return table


def star_construction(n):
    q, remainder = divmod(n, 4)
    require(q >= 1, "Construction requires n >= 4")
    block_sizes = [4] * (q - 1) + [4 + remainder]
    blocks, edges = [], []
    offset = 0
    for size in block_sizes:
        block = tuple(range(offset, offset + size))
        blocks.append(block)
        edges.extend((block[0], leaf) for leaf in block[1:])
        offset += size
    require(offset == n and len(edges) == n - q, "Partition count failed")
    require(tuple(i for block in blocks for i in block) == tuple(range(n)),
            "Partition does not cover coordinates exactly")
    return blocks, tuple(edges)


def verify_small_structural_collisions(n, vertices, distances):
    """All allowed outside landmarks are tested, not just one selected R."""
    index = {vertex: i for i, vertex in enumerate(vertices)}
    cases = 0

    def verify_collision(left, right, allowed_landmarks):
        nonlocal cases
        require(left != right and left in index and right in index,
                "Invalid collision vertices")
        row_left, row_right = distances[index[left]], distances[index[right]]
        for landmark in allowed_landmarks:
            require(row_left[index[landmark]] == row_right[index[landmark]],
                    "Structural collision failed")
        cases += 1

    # i is an unmarked isolated coordinate, j is any other unmarked one.
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            allowed = []
            for landmark in vertices:
                occupied = support(landmark)
                if len(occupied) == 2 and i not in occupied:
                    allowed.append(landmark)
                elif len(occupied) == 1 and occupied[0] not in (i, j):
                    allowed.append(landmark)
            verify_collision(token_vertex(n, (j, j)),
                             token_vertex(n, (i, j)), allowed)

    # An unmarked two-vertex component has its single edge plus arbitrary
    # landmarks wholly outside its coordinates.
    for i, j in combinations(range(n), 2):
        allowed = [token_vertex(n, (i, j))]
        allowed.extend(r for r in vertices if r[i] == r[j] == 0)
        verify_collision(token_vertex(n, (i, i)),
                         token_vertex(n, (j, j)), allowed)

    # An unmarked three-vertex tree is a path with a chosen middle b.
    for triple in combinations(range(n), 3):
        for b in triple:
            a, c = [v for v in triple if v != b]
            allowed = [token_vertex(n, (a, b)), token_vertex(n, (b, c))]
            allowed.extend(r for r in vertices if all(r[i] == 0 for i in triple))
            verify_collision(token_vertex(n, (b, b)),
                             token_vertex(n, (a, c)), allowed)
    return cases


def main():
    n, k = 8, 2
    require(type(n) is int and type(k) is int and n >= 1 and k >= 1,
            "Source parameter domain failed")
    vertices = vertices_k2(n)
    require(len(vertices) == comb(n + k - 1, k) == 36,
            "Incorrect complete vertex count")
    require(len(set(vertices)) == len(vertices), "Repeated vertex")
    require(all(len(v) == n and all(type(a) is int and a >= 0 for a in v)
                and sum(v) == k for v in vertices), "Inadmissible vertex")
    require(len(set(map(support, vertices))) == len(vertices),
            "Support does not identify a k=2 vertex")
    index = {vertex: i for i, vertex in enumerate(vertices)}

    distances, graph_edges = token_move_distances(vertices)
    formula_checks = 0
    pair_measurement_checks = 0
    for i, left in enumerate(vertices):
        for j, right in enumerate(vertices):
            require(distances[i][j] == exact_distance(left, right),
                    "BFS and half-L1 disagree")
            overlap = sum(min(a, b) for a, b in zip(left, right))
            require(distances[i][j] == k - overlap,
                    "BFS and overlap formula disagree")
            formula_checks += 1
        for a, b in combinations(range(n), 2):
            landmark = token_vertex(n, (a, b))
            require(2 - distances[i][index[landmark]] ==
                    int(left[a] > 0) + int(left[b] > 0),
                    "Pair landmark support measurement failed")
            pair_measurement_checks += 1

    # All block sizes used by the general construction: 4, 5, 6, and 7.
    local_sizes = {}
    for leaf_count in range(3, 7):
        table = local_table(leaf_count)
        expected = 1 + leaf_count + 1 + comb(leaf_count + 1, 2)
        require(len(table) == expected, "Incomplete local support table")
        local_sizes[str(leaf_count)] = len(table)

    blocks, landmark_pairs = star_construction(n)
    require(landmark_pairs == ((0, 1), (0, 2), (0, 3),
                              (4, 5), (4, 6), (4, 7)),
            "Witness differs from explicit submitted landmarks")
    landmarks = tuple(token_vertex(n, pair) for pair in landmark_pairs)
    require(len(landmarks) == len(set(landmarks)) == 6,
            "Incorrect number of distinct landmarks")
    require(all(r in index for r in landmarks), "Inadmissible landmark")
    landmark_indices = tuple(index[r] for r in landmarks)
    signatures = tuple(tuple(distances[i][j] for j in landmark_indices)
                       for i in range(len(vertices)))
    require(len(set(signatures)) == 36, "Witness fails to resolve all vertices")

    pairs = tuple(combinations(range(len(vertices)), 2))
    require(len(pairs) == comb(36, 2) == 630, "Incorrect vertex pair count")
    require(all(any(distances[i][j] != distances[h][j]
                    for j in landmark_indices) for i, h in pairs),
            "Unseparated pair of vertices")

    decoded = 0
    for vertex, signature in zip(vertices, signatures):
        recovered_support = []
        offset = 0
        for block in blocks:
            count = len(block) - 1
            measurement = tuple(2 - d for d in signature[offset:offset + count])
            occupied = local_table(count)[measurement]
            recovered_support.extend(block[j] for j in occupied)
            offset += count
        require(tuple(recovered_support) == support(vertex), "Support decode failed")
        if len(recovered_support) == 1:
            reconstructed = token_vertex(n, (recovered_support[0],) * 2)
        else:
            require(len(recovered_support) == 2, "Unexpected global support size")
            reconstructed = token_vertex(n, recovered_support)
        require(reconstructed == vertex, "Vertex reconstruction failed")
        decoded += 1

    # A bit represents an unordered vertex pair. For each possible landmark,
    # set precisely the bits for pairs it fails to distinguish. The intersection
    # is nonempty exactly when the selected landmarks fail to resolve the graph.
    unresolved_masks = []
    for landmark_index in range(len(vertices)):
        mask = 0
        for bit, (i, j) in enumerate(pairs):
            if distances[i][landmark_index] == distances[j][landmark_index]:
                mask |= 1 << bit
        unresolved_masks.append(mask)
    candidate_count = 0
    collision_certificates_checked = 0
    for candidate in combinations(range(len(vertices)), 5):
        common = (1 << len(pairs)) - 1
        for landmark_index in candidate:
            common &= unresolved_masks[landmark_index]
        require(common != 0, "Found a resolving set of five landmarks")
        # Recover a concrete surviving pair and verify its five equalities.
        bit = (common & -common).bit_length() - 1
        i, j = pairs[bit]
        require(i != j and all(distances[i][r] == distances[j][r] for r in candidate),
                "Invalid candidate-specific nonresolution witness")
        candidate_count += 1
        collision_certificates_checked += 1
    require(candidate_count == comb(36, 5) == 376992,
            "Incomplete five-landmark enumeration")
    # Any smaller resolving set could be enlarged to five distinct vertices;
    # adding landmarks preserves every distance separation already present.
    minimum_dimension = 6
    require(len(landmarks) == minimum_dimension < n - 1,
            "Original conjectured conclusion not violated")

    collision_cases = verify_small_structural_collisions(n, vertices, distances)
    # Supplementary finite checks across all residue classes; these are not
    # substitutes for the unbounded partition and component proofs.
    tested_n = []
    for size in range(4, 17):
        block_list, edge_list = star_construction(size)
        instance_vertices = vertices_k2(size)
        instance_landmarks = [token_vertex(size, pair) for pair in edge_list]
        instance_signatures = {
            tuple(exact_distance(v, r) for r in instance_landmarks)
            for v in instance_vertices
        }
        require(len(instance_signatures) == len(instance_vertices),
                "Supplementary star construction collision")
        tested_n.append(size)

    print(json.dumps({
        "status": "PASS",
        "arithmetic": "integers only",
        "n": n,
        "k": k,
        "vertex_count": len(vertices),
        "token_move_edge_count": graph_edges,
        "ordered_BFS_distance_formula_checks": formula_checks,
        "pair_landmark_measurement_checks": pair_measurement_checks,
        "local_support_patterns_by_leaf_count": local_sizes,
        "landmarks_1_based": [[a + 1, b + 1] for a, b in landmark_pairs],
        "landmark_vectors": landmarks,
        "distinct_signatures": len(set(signatures)),
        "separated_unordered_vertex_pairs": len(pairs),
        "decoded_vertices": decoded,
        "five_landmark_subsets_checked": candidate_count,
        "five_landmark_resolving_sets": 0,
        "candidate_collision_certificates_checked": collision_certificates_checked,
        "structural_collision_cases_checked": collision_cases,
        "supplementary_star_construction_n": tested_n,
        "certified_dimension": minimum_dimension,
        "conjectured_dimension": n - 1,
        "conjecture_violated": True,
        "complete_distance_certificate": [
            {"vertex": vertex, "signature": signature}
            for vertex, signature in zip(vertices, signatures)
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
