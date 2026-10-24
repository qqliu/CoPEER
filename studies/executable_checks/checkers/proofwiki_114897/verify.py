r'''The proof asserts that the least element ⊥ of a Boolean algebra "is contained in every filter" (used to conclude that the family 𝓕_a of filters containing a is nonempty). This is false: ⊥ lies in a filter only if that filter is the whole algebra, so no proper filter contains ⊥. A closely related load-bearing claim on line 0039 ("if 𝓕 is a proper filter containing a, then 𝓕 is not maximal") is refuted by the same kind of finite witness.'''

import json
from itertools import combinations, product

record_id = "proofwiki_114897"
confirmed_notes = "Exact recomputation confirms that in B=P({0}), F={{0}} is a proper filter omitting ⊥=∅. Taking a={0}, F contains a and is maximal among proper filters, so it also refutes the related maximality assertion. The quoted “⊥ lies in every filter” statement is plainly a ⊥/⊤ typo; the related maximality assertion is substantively false."
invalid_notes = "The proposed witness did not pass the independent exact checks."

bottom = frozenset()
top = frozenset({0})
algebra = frozenset({bottom, top})
witness = frozenset({top})
a = top


def meet(x, y):
    return x.intersection(y)


def join(x, y):
    return x.union(y)


def complement(x):
    return top.difference(x)


def families(carrier):
    ordered = tuple(carrier)
    for size in range(len(ordered) + 1):
        for chosen in combinations(ordered, size):
            yield frozenset(chosen)


def is_filter(family):
    if top not in family:
        return False
    for x, y in product(family, repeat=2):
        if meet(x, y) not in family:
            return False
    for x in family:
        for y in algebra:
            if x.issubset(y) and y not in family:
                return False
    return True


closed = all(
    meet(x, y) in algebra
    and join(x, y) in algebra
    and complement(x) in algebra
    for x, y in product(algebra, repeat=2)
)
complemented = all(
    meet(x, complement(x)) == bottom
    and join(x, complement(x)) == top
    for x in algebra
)
distributive = all(
    meet(x, join(y, z)) == join(meet(x, y), meet(x, z))
    and join(x, meet(y, z)) == meet(join(x, y), join(x, z))
    for x, y, z in product(algebra, repeat=3)
)

all_families = tuple(families(algebra))
proper_filters = tuple(
    family for family in all_families
    if is_filter(family) and family != algebra
)
maximal = is_filter(witness) and witness != algebra and not any(
    witness < larger and larger != algebra and is_filter(larger)
    for larger in all_families
)
bottom_forces_whole = all(
    bottom not in family or family == algebra
    for family in all_families
    if is_filter(family)
)

established = (
    algebra == frozenset({frozenset(), frozenset({0})})
    and closed
    and complemented
    and distributive
    and witness in proper_filters
    and bottom not in witness
    and a in witness
    and maximal
    and bottom_forces_whole
)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if established else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if established else invalid_notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
