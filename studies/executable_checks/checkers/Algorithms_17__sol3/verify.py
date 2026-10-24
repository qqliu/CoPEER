r"""() If G is not acyclic, then G has multiple transitive reductions."""

import json
from itertools import combinations

REPORT = {
    "record_id": "Algorithms_17__sol3",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not plainly a typo: the directed 2-cycle is cyclic, and its only reachability-preserving spanning subgraph is itself, so its transitive reduction is unique.",
}

vertices = (0, 1)
witness = frozenset(((0, 1), (1, 0)))


def reachability(edges):
    result = set()
    for source in vertices:
        pending = [end for start, end in edges if start == source]
        seen = set()
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            result.add((source, current))
            pending.extend(
                end
                for start, end in edges
                if start == current and end not in seen
            )
    return frozenset(result)


target = reachability(witness)
assert target == frozenset(((0, 0), (0, 1), (1, 0), (1, 1)))
assert any((vertex, vertex) in target for vertex in vertices)

ordered_edges = tuple(sorted(witness))
candidates = tuple(
    frozenset(selected)
    for size in range(len(ordered_edges) + 1)
    for selected in combinations(ordered_edges, size)
)
equivalent = tuple(candidate for candidate in candidates if reachability(candidate) == target)
assert equivalent == (witness,)
assert all(
    reachability(candidate) != target
    for candidate in candidates
    if candidate < witness
)

minimal_reductions = tuple(
    candidate
    for candidate in equivalent
    if not any(other < candidate and reachability(other) == target for other in candidates)
)
minimum_size = min(len(candidate) for candidate in equivalent)
minimum_reductions = tuple(
    candidate for candidate in equivalent if len(candidate) == minimum_size
)
assert minimal_reductions == (witness,)
assert minimum_reductions == (witness,)

print(json.dumps(REPORT, separators=(",", ":")))
