r"""Assume, for the sake of contradiction, that both $G$ and $\bar G$ are nonplanar. Then $$\lvert{E(G)}\rvert+\lvert{E(\bar G)}\rvert \le (3\lvert{V(G)}\rvert-6)+(3\lvert{V(\bar G)}\rvert-6)=54. \Rightarrow\Leftarrow$$"""

import json

record_id = "SE_math_2261418__q"
confirmed_notes = ("Exact recomputation confirms the witness: G has 19 edges and "
                   "contains K5; its 36-edge complement contains K3,3; hence both "
                   "are nonplanar, while 55 > 54. The refuted statement is plainly "
                   "a typo: the planar edge bound was applied under an assumption "
                   "of nonplanarity.")

vertices = tuple(range(11))
g_edges = set()
for u in vertices:
    for v in vertices:
        if u < v:
            in_first_block = u <= 4 and v <= 4
            across_later_blocks = 5 <= u <= 7 and 8 <= v <= 10
            if in_first_block or across_later_blocks:
                g_edges.add((u, v))

all_edges = set()
for u in vertices:
    for v in vertices:
        if u < v:
            all_edges.add((u, v))
complement_edges = all_edges.difference(g_edges)

k5_vertices = (0, 1, 2, 3, 4)
k5_present = True
for i in range(len(k5_vertices)):
    for j in range(i + 1, len(k5_vertices)):
        if (k5_vertices[i], k5_vertices[j]) not in g_edges:
            k5_present = False

left = (0, 1, 2)
right = (5, 6, 7)
k33_present = True
for u in left:
    for v in right:
        edge = (u, v) if u < v else (v, u)
        if edge not in complement_edges:
            k33_present = False

edge_counts_correct = len(g_edges) == 19 and len(complement_edges) == 36
partition_correct = g_edges.isdisjoint(complement_edges) and g_edges.union(complement_edges) == all_edges
rhs = (3 * len(vertices) - 6) + (3 * len(vertices) - 6)
inequality_holds = len(g_edges) + len(complement_edges) <= rhs
witness_valid = (k5_present and k33_present and edge_counts_correct and
                 partition_correct and rhs == 54 and not inequality_holds)

if witness_valid:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = ("Independent exact recomputation did not validate the reported witness. "
             "The statement nevertheless appears plainly mistyped because its edge "
             "bound is a planar-graph bound used under a nonplanarity assumption.")

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes},
                 separators=(",", ":")))
