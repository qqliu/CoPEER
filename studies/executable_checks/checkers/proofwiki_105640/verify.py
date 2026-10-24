r'''That $N \cap F = \O$ follows from the hypotheses actually stated (distributive lattice $L$, filter $F$, ideal $M$ disjoint from $F$ and maximal among ideals disjoint from $F$, $N = \set{x : \exists m \in M: x \le m \vee a}$, with $a$ an arbitrary element of $L$). The proof closes only by invoking the extra, unstated assumption "$\forall m \in M: m \vee a \notin F$"; without that assumption the conclusion is false, and a two-element lattice witnesses the failure.'''

import json

universe = frozenset({0, 1})
order_pairs = frozenset({(0, 0), (0, 1), (1, 1)})
meet_table = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1}
join_table = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 1}


def below(x, y):
    return (x, y) in order_pairs


def meet(x, y):
    return meet_table[(x, y)]


def join(x, y):
    return join_table[(x, y)]


def lattice_is_valid():
    reflexive = all(below(x, x) for x in universe)
    antisymmetric = all(
        not (below(x, y) and below(y, x)) or x == y
        for x in universe for y in universe
    )
    transitive = all(
        not (below(x, y) and below(y, z)) or below(x, z)
        for x in universe for y in universe for z in universe
    )
    extrema = all(
        below(meet(x, y), x)
        and below(meet(x, y), y)
        and all(not (below(t, x) and below(t, y)) or below(t, meet(x, y)) for t in universe)
        and below(x, join(x, y))
        and below(y, join(x, y))
        and all(not (below(x, t) and below(y, t)) or below(join(x, y), t) for t in universe)
        for x in universe for y in universe
    )
    distributive = all(
        meet(x, join(y, z)) == join(meet(x, y), meet(x, z))
        and join(x, meet(y, z)) == meet(join(x, y), join(x, z))
        for x in universe for y in universe for z in universe
    )
    return reflexive and antisymmetric and transitive and extrema and distributive


def filter_property(part):
    return bool(part) and all(
        meet(x, y) in part for x in part for y in part
    ) and all(
        not below(x, y) or y in part for x in part for y in universe
    )


def ideal_property(part):
    return bool(part) and all(
        join(x, y) in part for x in part for y in part
    ) and all(
        not below(y, x) or y in part for x in part for y in universe
    )


all_parts = (
    frozenset(),
    frozenset({0}),
    frozenset({1}),
    frozenset({0, 1}),
)
F = frozenset({1})
M = frozenset({0})
a = 1
ideals = tuple(part for part in all_parts if ideal_property(part))
maximal_disjoint = not any(
    M < candidate and candidate.isdisjoint(F) for candidate in ideals
)
N = frozenset(
    x for x in universe
    if any(below(x, join(m, a)) for m in M)
)
valid = (
    lattice_is_valid()
    and filter_property(F)
    and ideal_property(M)
    and M.isdisjoint(F)
    and maximal_disjoint
    and N == universe
    and N.intersection(F) == frozenset({1})
)

verdict = "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID"
notes = (
    "Independent exact recomputation validates the two-element-chain witness: all stated hypotheses hold, N={0,1}, and N∩F={1}. The refuted statement is substantive, not plainly a typo: it requires the missing assumption."
    if valid else
    "Independent exact recomputation did not validate the proposed witness. The refuted statement would be substantive rather than plainly a typo."
)
print(json.dumps({
    "record_id": "proofwiki_105640",
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":"), ensure_ascii=False))
