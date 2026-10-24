r'''That $N \cap F = \O$ follows from the hypotheses actually stated (distributive lattice $L$, filter $F$, ideal $M$ disjoint from $F$ and maximal among ideals disjoint from $F$, $N = \set{x : \exists m \in M: x \le m \vee a}$, with $a$ an arbitrary element of $L$). The proof closes only by invoking the extra, unstated assumption "$\forall m \in M: m \vee a \notin F$"; without that assumption the conclusion is false, and a two-element lattice witnesses the failure.'''

import json

L = (0, 1)


def meet(x, y):
    return min(x, y)


def join(x, y):
    return max(x, y)


def leq(x, y):
    return x <= y


def subsets():
    return tuple(
        frozenset(x for index, x in enumerate(L) if mask & (1 << index))
        for mask in range(1 << len(L))
    )


def is_filter(candidate):
    return bool(candidate) and all(
        (not leq(x, y)) or y in candidate
        for x in candidate
        for y in L
    ) and all(
        meet(x, y) in candidate
        for x in candidate
        for y in candidate
    )


def is_ideal(candidate):
    return bool(candidate) and all(
        (not leq(y, x)) or y in candidate
        for x in candidate
        for y in L
    ) and all(
        join(x, y) in candidate
        for x in candidate
        for y in candidate
    )


def is_distributive():
    return all(
        meet(x, join(y, z)) == join(meet(x, y), meet(x, z))
        and join(x, meet(y, z)) == meet(join(x, y), join(x, z))
        for x in L
        for y in L
        for z in L
    )


all_subsets = subsets()
all_ideals = tuple(candidate for candidate in all_subsets if is_ideal(candidate))
assert is_distributive()

witnesses = []
triples_checked = 0
for F in all_subsets:
    for M in all_subsets:
        for a in L:
            triples_checked += 1
            hypotheses = (
                is_filter(F)
                and is_ideal(M)
                and M.isdisjoint(F)
                and not any(
                    M < larger and larger.isdisjoint(F)
                    for larger in all_ideals
                )
            )
            if hypotheses:
                N = frozenset(
                    x for x in L
                    if any(leq(x, join(m, a)) for m in M)
                )
                if not N.isdisjoint(F):
                    witnesses.append((F, M, a, N, N & F))

assert triples_checked == 32
assert witnesses
assert witnesses[0] == (
    frozenset((1,)),
    frozenset((0,)),
    1,
    frozenset((0, 1)),
    frozenset((1,)),
)

result = {
    "record_id": "proofwiki_105640",
    "outcome": "WITNESS_FOUND",
    "witness_description": "In the two-element chain L={0,1}, take F={1}, M={0}, and a=1. Then N={0,1}, so 1 belongs to N cap F.",
    "refutation_explanation": "L is distributive; F={1} is a filter; M={0} is an ideal disjoint from F and is maximal among such ideals, since its only strictly larger ideal is L, which meets F. For m=0, m join a=1, and every x in L satisfies x<=1. Hence N=L and N cap F={1}, not the empty set.",
    "search_space": "All 32 triples (F, M, a), with F and M ranging over all 4 subsets of the fixed two-element chain L={0,1} and a ranging over {0,1}; the hypotheses and N were checked exactly for every triple.",
}
print(json.dumps(result, separators=(",", ":")))
