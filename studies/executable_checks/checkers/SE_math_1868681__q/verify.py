r"""Therefore the formula for the greatest number of edges on a bipartite graph on $p$ edges is $\frac{p^2}{4}$."""

import json

record_id = "SE_math_1868681__q"
notes = ("Exact recomputation confirms the literal claim fails at p=1: the simple "
         "graph with vertices 0 and 1 and edge {0,1} is bipartite, has p=1 edge, "
         "and 1 > 1^2/4. The refuted wording is plainly a typo: it almost certainly "
         "intended “p vertices,” not “p edges” (and even then an integer floor is needed).")

vertices = frozenset((0, 1))
edges = frozenset((frozenset((0, 1)),))
left_part = frozenset((0,))
right_part = frozenset((1,))
p = 1

valid_simple_graph = all(len(edge) == 2 and edge <= vertices for edge in edges)
valid_partition = (
    left_part.isdisjoint(right_part)
    and left_part | right_part == vertices
    and all(
        len(edge & left_part) == 1 and len(edge & right_part) == 1
        for edge in edges
    )
)
fixed_edge_count = len(edges) == p
exceeds_claim = 4 * len(edges) > p * p
verified = valid_simple_graph and valid_partition and fixed_edge_count and exceeds_claim
verdict = "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID"

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes},
                 separators=(",", ":"), ensure_ascii=False))
