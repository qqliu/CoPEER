r"""Every pair of distinct vertices in a bridgeless graph has two internally disjoint paths between them."""

import json

RECORD_ID = "arxiv_1201.5203v4__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = "Exact recomputation confirms the connected witness has no bridges, while deleting vertex 0 separates vertices 1 and 3; therefore every 1–3 path has internal vertex 0 and no two are internally disjoint. The refuted statement is substantive as written—it confuses edge-connectivity with vertex-connectivity—and is not plainly a typo from the permitted evidence."

vertices = frozenset((0, 1, 2, 3, 4))
edges = frozenset((
    frozenset((0, 1)),
    frozenset((1, 2)),
    frozenset((0, 2)),
    frozenset((0, 3)),
    frozenset((3, 4)),
    frozenset((0, 4)),
))


def reachable(start, excluded_vertex=None, excluded_edge=None):
    if start == excluded_vertex:
        return frozenset()
    seen = {start}
    pending = [start]
    while pending:
        current = pending.pop()
        for edge in edges:
            if edge == excluded_edge or current not in edge:
                continue
            for neighbor in edge:
                if neighbor != current and neighbor != excluded_vertex and neighbor not in seen:
                    seen.add(neighbor)
                    pending.append(neighbor)
    return frozenset(seen)


assert len(vertices) == 5
assert len(edges) == 6
assert all(len(edge) == 2 and edge <= vertices for edge in edges)
assert reachable(0) == vertices
assert all(reachable(0, excluded_edge=edge) == vertices for edge in edges)
assert 1 != 3 and 0 not in (1, 3)
assert 3 not in reachable(1, excluded_vertex=0)
assert 3 in reachable(1)

result = {
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
