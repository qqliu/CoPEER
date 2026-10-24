r"""Lemma 4 (Chartrand and Harary 1967). A planar graph is outerplanar if and only if its blocks are outerplanar and its block-cutpoint tree is a path."""

import itertools
import json

REPORT = {
    "record_id": "Graph Theory_10__sol5",
    "outcome": "WITNESS_FOUND",
    "witness_description": "On vertices {0,1,2,3}, take edges {0-1,0-2,0-3}; this is the star K_1,3.",
    "refutation_explanation": "This tree has an outerplane embedding with cyclic boundary order (0,1,2,3), and each of its three blocks is a single edge and hence outerplanar. Its block-cutpoint tree has one cutpoint node of degree 3 joined to the three block nodes, so it is not a path. Thus the left side of the claimed equivalence is true and the right side is false.",
    "search_space": "All 64 labeled simple graphs on vertex set {0,1,2,3}, in increasing 6-bit edge-mask order, with the counterexample test exhaustively applied to the connected 3-edge graphs (exactly the trees in this space).",
}

VERTICES = (0, 1, 2, 3)
ALL_EDGES = tuple(itertools.combinations(VERTICES, 2))


def make_adjacency(vertices, edges):
    lists = {vertex: [] for vertex in vertices}
    for left, right in edges:
        lists[left].append(right)
        lists[right].append(left)
    return {vertex: tuple(lists[vertex]) for vertex in vertices}


def component_count(vertices, adjacency, removed=None):
    seen = set()
    count = 0
    for start in vertices:
        if start == removed or start in seen:
            continue
        count += 1
        seen.add(start)
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor != removed and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


def is_tree(vertices, edges, adjacency):
    return len(edges) == len(vertices) - 1 and component_count(vertices, adjacency) == 1


def chords_cross(order, first, second):
    a, b = first
    c, d = second
    if len({a, b, c, d}) != 4:
        return False
    position = {vertex: index for index, vertex in enumerate(order)}
    pa, pb = position[a], position[b]
    if pb < pa:
        pa, pb = pb, pa
    c_inside = pa < position[c] < pb
    d_inside = pa < position[d] < pb
    return c_inside != d_inside


def convex_outerplane_order(vertices, edges):
    first_vertex = min(vertices)
    for order in itertools.permutations(vertices):
        if order[0] != first_vertex:
            continue
        crossing = False
        for first_index in range(len(edges)):
            for second_index in range(first_index + 1, len(edges)):
                if chords_cross(order, edges[first_index], edges[second_index]):
                    crossing = True
                    break
            if crossing:
                break
        if not crossing:
            return order
    return None


def block_cut_graph(vertices, edges, adjacency):
    cutpoints = tuple(
        vertex
        for vertex in vertices
        if component_count(vertices, adjacency, removed=vertex) > 1
    )
    block_nodes = tuple(("B", index) for index in range(len(edges)))
    cutpoint_nodes = tuple(("C", vertex) for vertex in cutpoints)
    nodes = block_nodes + cutpoint_nodes
    lists = {node: [] for node in nodes}
    for index, edge in enumerate(edges):
        block_node = ("B", index)
        for vertex in cutpoints:
            if vertex in edge:
                cutpoint_node = ("C", vertex)
                lists[block_node].append(cutpoint_node)
                lists[cutpoint_node].append(block_node)
    return nodes, {node: tuple(lists[node]) for node in nodes}


def is_path_graph(nodes, adjacency):
    if not nodes:
        return False
    seen = {nodes[0]}
    stack = [nodes[0]]
    while stack:
        current = stack.pop()
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    edge_count = sum(len(adjacency[node]) for node in nodes) // 2
    return (
        len(seen) == len(nodes)
        and edge_count == len(nodes) - 1
        and all(len(adjacency[node]) <= 2 for node in nodes)
    )


def counterexample_certificate(vertices, edges):
    adjacency = make_adjacency(vertices, edges)
    if not is_tree(vertices, edges, adjacency):
        return None

    outer_order = convex_outerplane_order(vertices, edges)
    if outer_order is None:
        return None

    blocks = tuple((edge,) for edge in edges)
    block_orders = tuple(
        convex_outerplane_order(block[0], block)
        for block in blocks
    )
    if any(order is None for order in block_orders):
        return None

    nodes, block_cut_adjacency = block_cut_graph(vertices, edges, adjacency)
    if is_path_graph(nodes, block_cut_adjacency):
        return None

    return outer_order, blocks, block_orders, nodes, block_cut_adjacency


mask_limit = 1 << len(ALL_EDGES)
violations = []
swept = 0
for mask in range(mask_limit):
    swept += 1
    edges = tuple(
        edge
        for index, edge in enumerate(ALL_EDGES)
        if mask & (1 << index)
    )
    certificate = counterexample_certificate(VERTICES, edges)
    if certificate is not None:
        violations.append((mask, edges, certificate))

assert swept == mask_limit
assert mask_limit == 64
assert violations

found_mask, found_edges, found_certificate = violations[0]
outer_order, blocks, block_orders, nodes, block_cut_adjacency = found_certificate
assert found_mask == 7
assert found_edges == ((0, 1), (0, 2), (0, 3))
assert outer_order == (0, 1, 2, 3)
assert blocks == (((0, 1),), ((0, 2),), ((0, 3),))
assert all(order is not None for order in block_orders)
assert ("C", 0) in nodes
assert len(block_cut_adjacency[("C", 0)]) == 3
assert not is_path_graph(nodes, block_cut_adjacency)

print(json.dumps(REPORT, separators=(",", ":")))
