r'''Re-adding the removed vertex u preserves, for the same vertex supplied by the inductive hypothesis in G', reachability from every vertex by a directed path of length at most 2.'''

import json


def paths_at_most_two(vertices, edges, start):
    reachable = {start}
    one_step = {b for a, b in edges if a == start}
    reachable.update(one_step)
    two_step = {
        b
        for middle in one_step
        for a, b in edges
        if a == middle
    }
    reachable.update(two_step)
    assert reachable <= set(vertices)
    return reachable


def every_vertex_reaches(vertices, edges, target):
    return all(target in paths_at_most_two(vertices, edges, start) for start in vertices)


u = 'u'
v = 'v'
full_vertices = (u, v)
full_edges = frozenset({(v, u)})
reduced_vertices = tuple(x for x in full_vertices if x != u)
reduced_edges = frozenset(
    (a, b) for a, b in full_edges if a != u and b != u
)

assert reduced_vertices == (v,)
assert reduced_edges == frozenset()
assert paths_at_most_two(reduced_vertices, reduced_edges, v) == {v}
assert every_vertex_reaches(reduced_vertices, reduced_edges, v)
assert paths_at_most_two(full_vertices, full_edges, u) == {u}
assert v not in paths_at_most_two(full_vertices, full_edges, u)
assert not every_vertex_reaches(full_vertices, full_edges, v)

REPORT = {
    'record_id': 'reddit_learnmath_7oq330',
    'verdict': 'CONFIRMED',
    'notes': "The witness is valid: in G' the sole vertex v reaches itself by a length-0 path, while in G with only v→u, vertex u cannot reach v by any directed path of length at most 2. The refuted statement is substantive, not plainly a typo.",
}

print(json.dumps(REPORT, ensure_ascii=False, separators=(',', ':')))
