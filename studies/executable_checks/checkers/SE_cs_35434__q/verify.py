"""If e belongs to a cycle, and it belongs to MST, doesn't it immediately imply that the MST has a cycle and therefore is not a tree?"""

import itertools
import json

record_id = "SE_cs_35434__q"
notes = ("The witness is valid: in the unit-weight triangle, (0,1) lies on an "
         "ambient-graph cycle and in the minimum spanning tree {(0,1),(0,2)}, "
         "while that tree is acyclic. The refuted statement is substantive, "
         "not a typo; it conflates an edge lying on a cycle in G with the "
         "entire cycle lying in the MST.")

vertices = frozenset((0, 1, 2))
e01 = frozenset((0, 1))
e02 = frozenset((0, 2))
e12 = frozenset((1, 2))
graph = frozenset((e01, e02, e12))
tree = frozenset((e01, e02))
weight = {e01: 1, e02: 1, e12: 1}


def reachable(edges, start):
    seen = {start}
    pending = [start]
    while pending:
        current = pending.pop()
        for edge in edges:
            if current in edge:
                for endpoint in edge:
                    if endpoint not in seen:
                        seen.add(endpoint)
                        pending.append(endpoint)
    return seen


def acyclic(edges):
    parent = {vertex: vertex for vertex in vertices}

    def root(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for edge in edges:
        left, right = tuple(edge)
        left_root = root(left)
        right_root = root(right)
        if left_root == right_root:
            return False
        parent[left_root] = right_root
    return True


def spanning_tree(edges):
    return (len(edges) == len(vertices) - 1
            and reachable(edges, 0) == set(vertices)
            and acyclic(edges))


alternatives = []
for chosen in itertools.combinations(graph, len(vertices) - 1):
    candidate = frozenset(chosen)
    if spanning_tree(candidate):
        alternatives.append(candidate)

witness_valid = (
    e01 in graph
    and e01 in tree
    and 1 in reachable(graph.difference((e01,)), 0)
    and spanning_tree(tree)
    and acyclic(tree)
    and alternatives
    and sum(weight[edge] for edge in tree)
        == min(sum(weight[edge] for edge in candidate)
               for candidate in alternatives)
)

if not witness_valid:
    raise AssertionError("independent exact verification failed")

print(json.dumps({"record_id": record_id,
                  "verdict": "CONFIRMED",
                  "notes": notes}, separators=(",", ":")))
