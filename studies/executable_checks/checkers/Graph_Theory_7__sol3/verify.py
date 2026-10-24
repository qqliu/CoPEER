r"""We claim that K = K union {v} is a kernel of D:
 Independence: Since K is independent in D and v has out-degree zero in D, there are
no edges between vertices in K."""

import json

vertices = frozenset(("v", "k"))
v = "v"
K = frozenset(("k",))
arcs = frozenset((("k", "v"),))


def internal_arcs(selected, relation):
    return frozenset(
        (tail, head)
        for tail, head in relation
        if tail in selected and head in selected
    )


def outgoing_arcs(vertex, relation):
    return frozenset(
        (tail, head)
        for tail, head in relation
        if tail == vertex
    )


assert v in vertices
assert v not in K
assert K < vertices
assert len(arcs) == 1
assert all(tail in vertices and head in vertices for tail, head in arcs)
assert all(tail != head for tail, head in arcs)
assert internal_arcs(K, arcs) == frozenset()
assert outgoing_arcs(v, arcs) == frozenset()
expanded = K | frozenset((v,))
assert expanded == vertices
assert internal_arcs(expanded, arcs) == arcs
assert internal_arcs(expanded, arcs) != frozenset()

REPORT = {
    "record_id": "Graph Theory_7__sol3",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: K={k} is independent and v has out-degree zero in the one-arc digraph k->v, while K union {v} is not independent. The refuted statement is substantive, not plainly a typo: it confuses zero out-degree with absence of incoming arcs.",
}

print(json.dumps(REPORT, separators=(",", ":")))
