r"""In every acyclic graph, after choosing one vertex v, there is a unique path from v to every other vertex, so a single breadth-first search colors the whole graph."""

import json
from collections import deque

vertices = {0, 1}
edges = set()
chosen_vertex = 0


def is_simple_undirected(vertex_set, edge_set):
    for edge in edge_set:
        if not isinstance(edge, tuple) or len(edge) != 2:
            return False
        left, right = edge
        if left not in vertex_set or right not in vertex_set or left == right:
            return False
    return True


def adjacency_map(vertex_set, edge_set):
    neighbors = {vertex: set() for vertex in vertex_set}
    for left, right in edge_set:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return neighbors


def has_cycle(neighbors):
    visited = set()

    def explore(vertex, parent):
        visited.add(vertex)
        for neighbor in neighbors[vertex]:
            if neighbor == parent:
                continue
            if neighbor in visited:
                return True
            if explore(neighbor, vertex):
                return True
        return False

    for vertex in neighbors:
        if vertex not in visited and explore(vertex, None):
            return True
    return False


def breadth_first_reachable(neighbors, start):
    reached = {start}
    pending = deque([start])
    while pending:
        vertex = pending.popleft()
        for neighbor in neighbors[vertex]:
            if neighbor not in reached:
                reached.add(neighbor)
                pending.append(neighbor)
    return reached


simple = is_simple_undirected(vertices, edges)
adjacency = adjacency_map(vertices, edges)
acyclic = simple and not has_cycle(adjacency)
reached = breadth_first_reachable(adjacency, chosen_vertex)
no_path_to_other_vertex = 1 not in reached
bfs_misses_part_of_graph = reached != vertices

established = (
    vertices == {0, 1}
    and edges == set()
    and chosen_vertex == 0
    and acyclic
    and no_path_to_other_vertex
    and bfs_misses_part_of_graph
    and reached == {0}
)
assert established

result = {
    "record_id": "reddit_learnmath_3e6sra",
    "verdict": "CONFIRMED",
    "notes": "Independent exact recomputation confirms the two-vertex edgeless simple undirected graph is acyclic, while BFS from 0 reaches only 0 and there is no path to 1. The refuted statement is substantive (it omits connectedness), not plainly a typo.",
}
print(json.dumps(result, separators=(",", ":")))
