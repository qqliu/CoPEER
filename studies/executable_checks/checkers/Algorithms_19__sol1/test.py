r"""Theorem A (Cycle-maximum uniqueness uniqueness of the MST). The following are equivalent: (i) G has a unique MST. (ii) For every cycle C subseteq G, the maximum-weight edge in C is unique."""

import json
from itertools import combinations, product

REPORT = {
    "record_id": "Algorithms_19__sol1",
    "outcome": "WITNESS_FOUND",
    "witness_description": "On vertices {0,1,2,3}, use edges 0-1, 0-2, 0-3 of weight 1 and edges 1-2, 2-3 of weight 2. Its unique MST is the weight-1 star {0-1,0-2,0-3}, but the cycle 0-1-2-3-0 has two maximum-weight edges, 1-2 and 2-3, both of weight 2.",
    "refutation_explanation": "Thus (i) is true while (ii) is false for this graph, so the claimed equivalence fails.",
    "search_space": "Exhaustively swept all 2^5 = 32 assignments of weights in {1,2} to the fixed simple graph on labeled vertices {0,1,2,3} with edges {0-1,0-2,0-3,1-2,2-3}. The topology's 10 three-edge subsets were all checked to enumerate its spanning trees, and all 31 nonempty edge subsets were checked to enumerate its cycles; each weight assignment was then evaluated on those complete lists."
}

VERTEX_COUNT = 4
EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (2, 3))


def is_tree(edge_indices):
    parent = list(range(VERTEX_COUNT))

    def find(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for edge_index in edge_indices:
        left, right = EDGES[edge_index]
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        parent[right_root] = left_root
    return all(find(vertex) == find(0) for vertex in range(VERTEX_COUNT))


def is_cycle(edge_indices):
    degree = [0] * VERTEX_COUNT
    adjacency = [[] for _ in range(VERTEX_COUNT)]
    for edge_index in edge_indices:
        left, right = EDGES[edge_index]
        degree[left] += 1
        degree[right] += 1
        adjacency[left].append(right)
        adjacency[right].append(left)

    active = [vertex for vertex in range(VERTEX_COUNT) if degree[vertex] != 0]
    if len(active) < 3 or any(degree[vertex] != 2 for vertex in active):
        return False

    seen = {active[0]}
    stack = [active[0]]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(active)


SPANNING_TREES = tuple(
    edge_indices
    for edge_indices in combinations(range(len(EDGES)), VERTEX_COUNT - 1)
    if is_tree(edge_indices)
)
CYCLES = tuple(
    edge_indices
    for size in range(1, len(EDGES) + 1)
    for edge_indices in combinations(range(len(EDGES)), size)
    if is_cycle(edge_indices)
)


def minimum_trees(weights):
    weighted_trees = tuple(
        (sum(weights[index] for index in tree), tree)
        for tree in SPANNING_TREES
    )
    minimum_weight = min(weight for weight, tree in weighted_trees)
    return tuple(tree for weight, tree in weighted_trees if weight == minimum_weight)


def cycle_maximum_is_always_unique(weights):
    for cycle in CYCLES:
        cycle_weights = tuple(weights[index] for index in cycle)
        maximum = max(cycle_weights)
        if cycle_weights.count(maximum) != 1:
            return False
    return True


violations = []
for weights in product((1, 2), repeat=len(EDGES)):
    unique_mst = len(minimum_trees(weights)) == 1
    cycle_condition = cycle_maximum_is_always_unique(weights)
    if unique_mst != cycle_condition:
        violations.append((weights, unique_mst, cycle_condition))

assert violations
first_violation = violations[0]
assert first_violation == ((1, 1, 1, 2, 2), True, False)

witness_weights = first_violation[0]
assert minimum_trees(witness_weights) == ((0, 1, 2),)
witness_cycle = (0, 2, 3, 4)
assert witness_cycle in CYCLES
witness_cycle_weights = tuple(witness_weights[index] for index in witness_cycle)
assert witness_cycle_weights == (1, 1, 2, 2)
assert witness_cycle_weights.count(max(witness_cycle_weights)) == 2

print(json.dumps(REPORT, separators=(",", ":")))
