r"""Lemma 4 (Chartrand and Harary 1967). A planar graph is outerplanar if and only if its blocks are outerplanar and its block-cutpoint tree is a path."""

import json

REPORT = {
    "record_id": "Graph Theory_10__sol5",
    "verdict": "CONFIRMED",
    "notes": "The refutation is substantive, not plainly a typo: K_1,3 is outerplanar, all three blocks are K_2 and outerplanar, while its block-cutpoint tree is K_1,3 rather than a path.",
}

vertices = (0, 1, 2, 3)
edges = ((0, 1), (0, 2), (0, 3))
coordinates = ((0, 0), (2, 0), (2, 2), (0, 2))
boundary_order = (0, 1, 2, 3)

assert set(vertices) == {0, 1, 2, 3}
assert edges == ((0, 1), (0, 2), (0, 3))
assert all(left in vertices and right in vertices and left != right for left, right in edges)
assert len({frozenset(edge) for edge in edges}) == len(edges)


def orientation(first, second, third):
    return (
        (second[0] - first[0]) * (third[1] - first[1])
        - (second[1] - first[1]) * (third[0] - first[0])
    )


# The four integer points form a strictly convex quadrilateral in the stated
# boundary order. Every pair of witness edges shares only vertex 0, and their
# rays from 0 are non-collinear, so their straight-line interiors are disjoint.
turns = tuple(
    orientation(
        coordinates[boundary_order[index]],
        coordinates[boundary_order[(index + 1) % len(boundary_order)]],
        coordinates[boundary_order[(index + 2) % len(boundary_order)]],
    )
    for index in range(len(boundary_order))
)
convex_boundary = all(turn > 0 for turn in turns)
pairwise_clean = True
for first_index in range(len(edges)):
    for second_index in range(first_index + 1, len(edges)):
        first = edges[first_index]
        second = edges[second_index]
        common = set(first).intersection(second)
        if len(common) != 1:
            pairwise_clean = False
            continue
        pivot = next(iter(common))
        first_other = first[0] if first[1] == pivot else first[1]
        second_other = second[0] if second[1] == pivot else second[1]
        if orientation(
            coordinates[pivot],
            coordinates[first_other],
            coordinates[second_other],
        ) == 0:
            pairwise_clean = False

outerplanar = (
    tuple(sorted(boundary_order)) == vertices
    and convex_boundary
    and pairwise_clean
)
planar = outerplanar
assert outerplanar
assert planar


def component_count(removed_vertex=None, omitted_edge=None):
    active = tuple(vertex for vertex in vertices if vertex != removed_vertex)
    seen = set()
    count = 0
    for start in active:
        if start in seen:
            continue
        count += 1
        seen.add(start)
        stack = [start]
        while stack:
            current = stack.pop()
            for edge in edges:
                if edge == omitted_edge:
                    continue
                left, right = edge
                if left == current:
                    neighbor = right
                elif right == current:
                    neighbor = left
                else:
                    continue
                if neighbor != removed_vertex and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


base_components = component_count()
assert base_components == 1
assert len(edges) == len(vertices) - 1

bridges = tuple(
    edge
    for edge in edges
    if component_count(omitted_edge=edge) > base_components
)
assert bridges == edges

# In a connected graph every bridge is a K_2 block. Since every edge here is a
# bridge, these are all the blocks; each K_2 has an immediate outerplane drawing.
blocks = tuple((edge,) for edge in bridges)
assert blocks == (((0, 1),), ((0, 2),), ((0, 3),))
blocks_are_outerplanar = all(
    len(block) == 1 and len(frozenset(block[0])) == 2
    for block in blocks
)
assert blocks_are_outerplanar

cutpoints = tuple(
    vertex
    for vertex in vertices
    if component_count(removed_vertex=vertex) > base_components
)
assert cutpoints == (0,)
assert component_count(removed_vertex=0) == 3
assert all(component_count(removed_vertex=leaf) == 1 for leaf in (1, 2, 3))

block_nodes = tuple(("block", index) for index in range(len(blocks)))
cutpoint_nodes = tuple(("cutpoint", vertex) for vertex in cutpoints)
nodes = block_nodes + cutpoint_nodes
incidences = tuple(
    (block_nodes[block_index], cutpoint_nodes[cutpoint_index])
    for block_index in range(len(blocks))
    for cutpoint_index in range(len(cutpoints))
    if cutpoints[cutpoint_index] in blocks[block_index][0]
)
assert len(nodes) == 4
assert len(incidences) == 3

seen_nodes = {nodes[0]}
node_stack = [nodes[0]]
while node_stack:
    current = node_stack.pop()
    for left, right in incidences:
        if left == current:
            neighbor = right
        elif right == current:
            neighbor = left
        else:
            continue
        if neighbor not in seen_nodes:
            seen_nodes.add(neighbor)
            node_stack.append(neighbor)

incidence_connected = len(seen_nodes) == len(nodes)
degrees = tuple(
    sum(1 for incidence in incidences if node in incidence)
    for node in nodes
)
assert incidence_connected
assert len(incidences) == len(nodes) - 1
assert degrees == (1, 1, 1, 3)

block_cutpoint_tree_is_path = (
    incidence_connected
    and len(incidences) == len(nodes) - 1
    and all(degree <= 2 for degree in degrees)
)
assert not block_cutpoint_tree_is_path

left_side = outerplanar
right_side = blocks_are_outerplanar and block_cutpoint_tree_is_path
assert planar
assert left_side
assert not right_side
assert left_side != right_side
assert REPORT["record_id"] == "Graph Theory_10__sol5"
assert REPORT["verdict"] == "CONFIRMED"
assert REPORT["notes"] == "The refutation is substantive, not plainly a typo: K_1,3 is outerplanar, all three blocks are K_2 and outerplanar, while its block-cutpoint tree is K_1,3 rather than a path."

print(json.dumps(REPORT, separators=(",", ":")))
