r"""We claim that K = K union {v} is a kernel of D:
 Independence: Since K is independent in D and v has out-degree zero in D, there are
no edges between vertices in K."""

import json

REPORT = {
    "record_id": "Graph Theory_7__sol3",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Witness: the loopless digraph D on vertices {v, k} with the single arc k->v, with K={k}.",
    "refutation_explanation": "K is independent, and v has out-degree zero, but K union {v} contains the arc k->v and is therefore not independent. Thus out-degree zero rules out arcs from v, not arcs into v.",
    "search_space": "All 4 loopless directed graphs on the labeled vertex set {v, k}, obtained by choosing any subset of the two possible arcs v->k and k->v, with v fixed as v and K fixed as {k}; all 4 were swept in mask order 0,1,2,3.",
}

vertices = ("v", "k")
possible_arcs = (("v", "k"), ("k", "v"))
v = "v"
K = frozenset(("k",))


def is_independent(vertex_set, arcs):
    return all(not (tail in vertex_set and head in vertex_set)
               for tail, head in arcs)


def has_out_degree_zero(vertex, arcs):
    return all(tail != vertex for tail, _head in arcs)


visited_masks = []
first_violation = None
for mask in range(1 << len(possible_arcs)):
    visited_masks.append(mask)
    arcs = tuple(
        possible_arcs[index]
        for index in range(len(possible_arcs))
        if mask & (1 << index)
    )
    premises_hold = is_independent(K, arcs) and has_out_degree_zero(v, arcs)
    conclusion_fails = not is_independent(K | frozenset((v,)), arcs)
    if premises_hold and conclusion_fails and first_violation is None:
        first_violation = (mask, arcs)

assert visited_masks == [0, 1, 2, 3]
assert first_violation == (2, (("k", "v"),))
witness_arcs = first_violation[1]
assert is_independent(K, witness_arcs)
assert has_out_degree_zero(v, witness_arcs)
assert not is_independent(K | frozenset((v,)), witness_arcs)
assert REPORT["outcome"] == "WITNESS_FOUND"

print(json.dumps(REPORT, separators=(",", ":")))
