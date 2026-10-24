r"""Theorem A (Cycle-maximum uniqueness uniqueness of the MST). The following are equivalent: (i) G has a unique MST. (ii) For every cycle C subseteq G, the maximum-weight edge in C is unique."""

import json

REPORT = {
    "record_id": "Algorithms_19__sol1",
    "verdict": "CONFIRMED",
    "notes": "Exact integer enumeration confirms the unique weight-3 MST and the 4-cycle's tied maximum. The refuted equivalence is substantive; the duplicated word 'uniqueness' in the title is plainly a typo."
}

vertices = (0, 1, 2, 3)
edges = (
    (0, 1, 1),
    (0, 2, 1),
    (0, 3, 1),
    (1, 2, 2),
    (2, 3, 2),
)


def connected(mask):
    reached = {0}
    changed = True
    while changed:
        changed = False
        for index, (left, right, weight) in enumerate(edges):
            if mask & (1 << index):
                if left in reached and right not in reached:
                    reached.add(right)
                    changed = True
                elif right in reached and left not in reached:
                    reached.add(left)
                    changed = True
    return len(reached) == len(vertices)


def edge_count(mask):
    count = 0
    for index in range(len(edges)):
        if mask & (1 << index):
            count += 1
    return count


def total_weight(mask):
    total = 0
    for index, edge in enumerate(edges):
        if mask & (1 << index):
            total += edge[2]
    return total


spanning_tree_costs = []
for mask in range(1 << len(edges)):
    if edge_count(mask) == len(vertices) - 1 and connected(mask):
        spanning_tree_costs.append((total_weight(mask), mask))

assert spanning_tree_costs
least_cost = min(item[0] for item in spanning_tree_costs)
minimum_masks = [mask for cost, mask in spanning_tree_costs if cost == least_cost]
assert least_cost == 3
assert minimum_masks == [7]
assert tuple(edges[index][:2] for index in range(len(edges)) if minimum_masks[0] & (1 << index)) == (
    (0, 1),
    (0, 2),
    (0, 3),
)
unique_mst = len(minimum_masks) == 1
assert unique_mst

cycle_vertices = (0, 1, 2, 3, 0)
cycle_weights = []
for position in range(len(cycle_vertices) - 1):
    left = cycle_vertices[position]
    right = cycle_vertices[position + 1]
    matches = []
    for edge_left, edge_right, weight in edges:
        if (edge_left == left and edge_right == right) or (edge_left == right and edge_right == left):
            matches.append(weight)
    assert len(matches) == 1
    cycle_weights.append(matches[0])

assert tuple(cycle_weights) == (1, 2, 2, 1)
cycle_maximum = max(cycle_weights)
assert cycle_maximum == 2
assert cycle_weights.count(cycle_maximum) == 2
condition_ii_is_refuted = cycle_weights.count(cycle_maximum) != 1
assert unique_mst and condition_ii_is_refuted

print(json.dumps(REPORT, separators=(",", ":")))
