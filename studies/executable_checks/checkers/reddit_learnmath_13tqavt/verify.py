r"""If F is not closed, then every convergent sequence in F has its limit in the complement F'."""

import json
from itertools import product

record_id = "reddit_learnmath_13tqavt"
space = frozenset((0, 1))
empty = frozenset()
topology = frozenset((empty, space))
f_set = frozenset((0,))
constant_value = 0
claimed_limit = 0


def satisfies_topology_axioms(points, open_sets):
    if frozenset() not in open_sets or points not in open_sets:
        return False

    for left in open_sets:
        for right in open_sets:
            if left.intersection(right) not in open_sets:
                return False

    listed = tuple(open_sets)
    for choices in product((False, True), repeat=len(listed)):
        union = frozenset()
        for chosen, open_set in zip(choices, listed):
            if chosen:
                union = union.union(open_set)
        if union not in open_sets:
            return False
    return True


def constant_sequence_has_limit(open_sets, value, limit):
    for open_set in open_sets:
        if limit in open_set and value not in open_set:
            return False
    return True


complement = space.difference(f_set)
valid_witness = (
    satisfies_topology_axioms(space, topology)
    and complement not in topology
    and constant_value in f_set
    and constant_sequence_has_limit(topology, constant_value, claimed_limit)
    and claimed_limit not in complement
)

confirmed_notes = (
    "The witness is valid. The refuted statement is substantively false, not "
    "plainly a typo: a constant sequence in a nonclosed set can converge to "
    "one of that set's own points."
)
invalid_notes = (
    "The reported witness did not satisfy all required conditions under exact "
    "recomputation. The statement would be substantive rather than plainly a typo."
)
result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if valid_witness else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if valid_witness else invalid_notes,
}
print(json.dumps(result, separators=(",", ":")))
