"""if the graph has $k$ edges, there are at most $k!$ paths that do not use the same edge more than once"""

import json
import math

record_id = "SE_cs_143__a153"
notes = "Confirmed on the two-edge star: it has three nonempty paths up to reversal, while 2! = 2; the refuted statement is substantive, not plainly a typo."

vertices = (0, 1, 2)
edges = frozenset({frozenset({0, 1}), frozenset({0, 2})})
paths = set()


def extend(vertex_sequence, used_edges):
    current = vertex_sequence[-1]
    for edge in edges:
        if edge in used_edges or current not in edge:
            continue
        following = next(vertex for vertex in edge if vertex != current)
        candidate = vertex_sequence + (following,)
        reverse = candidate[::-1]
        paths.add(min(candidate, reverse))
        extend(candidate, used_edges | {edge})


for start in vertices:
    extend((start,), frozenset())

expected = {(0, 1), (0, 2), (1, 0, 2)}
confirmed = (
    len(edges) == 2
    and paths == expected
    and len(paths) == 3
    and math.factorial(len(edges)) == 2
    and len(paths) > math.factorial(len(edges))
)

verdict = "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID"
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
