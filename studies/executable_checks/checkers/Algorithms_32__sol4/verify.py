r"""where Su (resp. Sv) denotes the set of vertices in the component of T -u (resp. T -v) containing v (resp. u). But then |Su| + |Sv| > n, whereas Su and Sv are disjoint subsets of V (T) (aside from u, v themselves) covering V (T) \ {u, v}, so |Su| + |Sv| = n -2 < n"""

import json

REPORT = {
    "record_id": "Algorithms_32__sol4",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation gives Su={1}, Sv={0,2}, and |Su|+|Sv|=3=n, so both the asserted >n and =n-2 conclusions fail. The refuted n-2 statement is plainly an endpoint-counting typo, not a substantive mathematical counterexample: the definitions include v in Su and u in Sv.",
}


def connected_part(allowed, links, seed):
    assert seed in allowed
    part = frozenset((seed,))
    while True:
        grown = set(part)
        for link in links:
            if link <= allowed and not link.isdisjoint(part):
                grown.update(link)
        next_part = frozenset(grown)
        if next_part == part:
            return part
        part = next_part


vertices = frozenset((0, 1, 2))
links = frozenset((frozenset((0, 1)), frozenset((0, 2))))
u = 0
v = 1
n = len(vertices)

assert n == 3
assert u != v
assert all(len(link) == 2 and link <= vertices for link in links)
assert len(links) == n - 1
assert connected_part(vertices, links, 0) == vertices

su = connected_part(vertices.difference((u,)), links, v)
sv = connected_part(vertices.difference((v,)), links, u)

assert su == frozenset((1,))
assert sv == frozenset((0, 2))
assert su.isdisjoint(sv)
assert su.difference((v,)).union(sv.difference((u,))) == vertices.difference((u, v))

total = len(su) + len(sv)
assert total == 3
assert total == n
assert total != n - 2
assert not total > n

print(json.dumps(REPORT, separators=(",", ":")))
