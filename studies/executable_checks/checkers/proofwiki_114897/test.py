"""The proof asserts that the least element ⊥ of a Boolean algebra "is contained in every filter" (used to conclude that the family 𝓕_a of filters containing a is nonempty). This is false: ⊥ lies in a filter only if that filter is the whole algebra, so no proper filter contains ⊥. A closely related load-bearing claim on line 0039 ("if 𝓕 is a proper filter containing a, then 𝓕 is not maximal") is refuted by the same kind of finite witness."""

import json

n = 1
carrier = tuple(range(1 << n))
bottom = 0
top = (1 << n) - 1


def is_filter(family):
    members = frozenset(family)
    if top not in members:
        return False
    for x in members:
        for y in carrier:
            if (x & y) == x and y not in members:
                return False
    for x in members:
        for y in members:
            if (x & y) not in members:
                return False
    return True


counterexamples = []
for family_mask in range(1 << len(carrier)):
    family = tuple(
        element
        for element in carrier
        if family_mask & (1 << element)
    )
    if is_filter(family) and bottom not in family:
        counterexamples.append((family_mask, family))

if counterexamples != [(2, (1,))]:
    raise RuntimeError("unexpected exhaustive-search result")

result = {
    "record_id": "proofwiki_114897",
    "outcome": "WITNESS_FOUND",
    "witness_description": "B=P({0})={∅,{0}} and F={{0}}. F contains the top {0}, is upward closed and closed under intersection, hence is a proper filter; its least element ∅ is not in F.",
    "refutation_explanation": "The bounded enumeration verifies F as a filter while 0 (representing ∅=⊥) is absent, directly falsifying the assertion that ⊥ is contained in every filter.",
    "search_space": "All 4 candidate families F ⊆ P({0}) in the two-element Boolean algebra P({0}), enumerated by family masks 0 through 3; filterhood was checked by top containment, upward closure, and meet closure."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
