"""The asserted equivalence between membership in the interior of the closure of the complement of A's closure and membership in that complement is false in general."""

import json
from itertools import combinations

RECORD_ID = "proofwiki_39530__codex_expansion"
NOTES = ("Exact finite-set recomputation validates the topology and witness: "
         "closure(A)={1}, its complement is {0}, closure({0})=X, and "
         "interior(X)=X, so x=1 satisfies the left side but not the right. "
         "The refuted equivalence is substantive, not plainly a typo.")


def subfamilies(family):
    items = tuple(family)
    for count in range(len(items) + 1):
        for chosen in combinations(items, count):
            yield chosen


def union_all(family):
    result = set()
    for member in family:
        result.update(member)
    return frozenset(result)


def intersection_all(family, universe):
    result = set(universe)
    for member in family:
        result.intersection_update(member)
    return frozenset(result)


def valid_topology(universe, open_sets):
    if frozenset() not in open_sets or universe not in open_sets:
        return False
    for family in subfamilies(open_sets):
        if union_all(family) not in open_sets:
            return False
    for left in open_sets:
        for right in open_sets:
            if left.intersection(right) not in open_sets:
                return False
    return True


def topological_interior(subset, open_sets):
    contained = (member for member in open_sets if member.issubset(subset))
    return union_all(contained)


def topological_closure(subset, universe, open_sets):
    closed_sets = tuple(universe.difference(member) for member in open_sets)
    containers = tuple(member for member in closed_sets if subset.issubset(member))
    return intersection_all(containers, universe)


universe = frozenset((0, 1))
open_sets = frozenset((frozenset(), frozenset((0,)), universe))
a_set = frozenset((1,))
point = 1

is_topology = valid_topology(universe, open_sets)
closed_a = topological_closure(a_set, universe, open_sets)
complement = universe.difference(closed_a)
closed_complement = topological_closure(complement, universe, open_sets)
left_set = topological_interior(closed_complement, open_sets)
left_membership = point in left_set
right_membership = point in complement

verified = (
    is_topology
    and closed_a == frozenset((1,))
    and complement == frozenset((0,))
    and closed_complement == universe
    and left_set == universe
    and left_membership
    and not right_membership
)
if not verified:
    raise AssertionError("The reported witness did not pass independent verification")

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": "CONFIRMED",
    "notes": NOTES
}, separators=(",", ":")))
