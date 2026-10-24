r"""However, a minimal cut in a subgraph like G[A] or G[B] is also a minimal cut in the entire graph G."""

import json
from itertools import combinations


REPORT = {
    "record_id": "Algorithms_33__sol4",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness is certified: the supplied quote does not define 'minimal cut', the kind of cut, or how a cut of G[A] or G[B] is identified with a cut of G.",
    "refutation_explanation": "With those semantics absent, no candidate can be classified as satisfying or violating the claim without adding definitions not present in the permitted data; the bounded sweep is therefore inconclusive.",
    "search_space": "Illustrative candidate space exhaustively generated: all 74 pairs (G,S) where G is a labeled simple undirected graph on {0,...,n-1} for n in {1,2,3} and S is any vertex subset. Every pair remained unclassified because cut semantics are unspecified; this sweep is not evidence for the claim.",
}

# The permitted quote provides no cut predicate or rule relating subgraph cuts
# to cuts of G. None is supplied here, because doing so would invent semantics.
cut_semantics = None
swept = 0
classified_count = 0
unresolved_count = 0
first_witness = None
seen = set()

for n in range(1, 4):
    vertices = tuple(range(n))
    possible_edges = tuple(combinations(vertices, 2))
    for graph_mask in range(1 << len(possible_edges)):
        graph_edges = tuple(
            edge
            for index, edge in enumerate(possible_edges)
            if graph_mask & (1 << index)
        )
        for subset_mask in range(1 << n):
            subset = tuple(
                vertex
                for vertex in vertices
                if subset_mask & (1 << vertex)
            )
            candidate = (n, graph_edges, subset)
            assert candidate not in seen
            seen.add(candidate)
            swept += 1

            if cut_semantics is None:
                unresolved_count += 1
                continue

            raise AssertionError("No unquoted cut semantics may be introduced")

expected = 0
for n in range(1, 4):
    edge_count = n * (n - 1) // 2
    expected += (1 << edge_count) * (1 << n)

assert swept == len(seen)
assert swept == expected
assert swept == 74
assert unresolved_count == swept
assert classified_count == 0
assert first_witness is None

if first_witness is not None:
    derived_outcome = "WITNESS_FOUND"
elif classified_count == swept:
    derived_outcome = "NO_WITNESS_EXHAUSTIVE"
else:
    derived_outcome = "NO_WITNESS_INCONCLUSIVE"

assert REPORT["outcome"] == derived_outcome
assert set(REPORT) == {
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
}

print(json.dumps(REPORT, separators=(",", ":"), ensure_ascii=True))
