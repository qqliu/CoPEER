"""For every x ∈ A, there exists some a ∈ x (and hence a ∈ ∪A)."""

import json


def powerset(items):
    """Return every subset in increasing bit-mask order."""
    return tuple(
        frozenset(items[index] for index in range(len(items)) if mask & (1 << index))
        for mask in range(1 << len(items))
    )


universe = ()
possible_sets = powerset(universe)
families = powerset(possible_sets)
witness = None
checked_families = 0

for family in families:
    checked_families += 1
    union_of_family = frozenset(
        element
        for element in universe
        if any(member in family and element in member for member in possible_sets)
    )
    for x in possible_sets:
        if x in family:
            exists_required_element = any(
                element in x and element in union_of_family
                for element in universe
            )
            if not exists_required_element and witness is None:
                witness = (family, x)

assert checked_families == 2
assert witness == (frozenset((frozenset(),)), frozenset())

result = {
    "record_id": "reddit_askmath_11gn0pk",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take A = {∅} and x = ∅. Then x ∈ A, but there is no element a ∈ x.",
    "refutation_explanation": "The universal claim requires an element of every member x of A. For A = {∅}, its member x = ∅ has no elements; moreover ∪A = ∅. Thus the required existential statement is false.",
    "search_space": "All 2 families A ⊆ P(U) for the fixed finite universe U = ∅—namely A = ∅ and A = {∅}—with every x ∈ A checked.",
}

print(json.dumps(result, ensure_ascii=False))
