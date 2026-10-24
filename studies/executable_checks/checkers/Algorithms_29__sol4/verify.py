"""PG visits n distinct vertices of G. There are only n original vertices in VH, so any set of n distinct vertices of G must include all the original vertices VH"""

import json

REPORT = {
    "record_id": "Algorithms_29__sol4",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation gives G={0,1}, VH={0}, and one distinct visited vertex {1}; all stated premises hold while VH is not included in the visited set. The refuted statement is substantive, not plainly a typo."
}

n = 1
g_vertices = frozenset(range(n + 1))
original_vertices = frozenset((min(g_vertices),))
pg_walk = tuple(
    vertex
    for vertex in sorted(g_vertices)
    if vertex not in original_vertices
)
visited_vertices = frozenset(pg_walk)

assert g_vertices == frozenset((0, 1))
assert original_vertices == frozenset((0,))
assert pg_walk == (1,)
assert len(original_vertices) == n
assert original_vertices <= g_vertices
assert len(pg_walk) == n
assert len(visited_vertices) == n
assert visited_vertices <= g_vertices
assert not original_vertices <= visited_vertices

premises_hold = (
    len(original_vertices) == n
    and original_vertices <= g_vertices
    and len(pg_walk) == n
    and len(visited_vertices) == n
    and visited_vertices <= g_vertices
)
claimed_conclusion = original_vertices <= visited_vertices
assert premises_hold
assert not claimed_conclusion

print(json.dumps(REPORT, separators=(",", ":")))
