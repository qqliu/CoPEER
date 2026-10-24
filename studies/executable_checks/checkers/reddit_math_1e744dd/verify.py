r"""Sigma-finiteness is necessary to ensure uniqueness of the measure extension to the completion."""

import json

INFINITY = ("infinite",)
SPACE = frozenset((0,))
EMPTY = frozenset()
SIGMA = frozenset((EMPTY, SPACE))


def measure(measurable_set):
    assert measurable_set in SIGMA
    if measurable_set == EMPTY:
        return 0
    return INFINITY


def extended_add(left, right):
    if left == INFINITY or right == INFINITY:
        return INFINITY
    return left + right


def union_all(sets):
    result = EMPTY
    for item in sets:
        result = result | item
    return result


def all_subsets(finite_set):
    result = [EMPTY]
    for point in tuple(finite_set):
        point_set = frozenset((point,))
        prior = tuple(result)
        result.extend(item | point_set for item in prior)
    return frozenset(result)


def belongs_to_completion(candidate):
    # Equivalent completion criterion: E subset A subset F with F minus E null.
    for lower in SIGMA:
        for upper in SIGMA:
            if lower <= candidate and candidate <= upper:
                if measure(upper - lower) == 0:
                    return True
    return False


# Verify the concrete measure. Every measurable set is either empty or SPACE.
assert all(item == EMPTY or item == SPACE for item in SIGMA)
assert measure(EMPTY) == 0
assert measure(SPACE) == INFINITY

# Exhaust disjoint measurable pairs. In any countable disjoint sequence there
# can consequently be at most one nonempty term; all remaining terms are empty.
binary_additivity = True
for left in SIGMA:
    for right in SIGMA:
        if left.isdisjoint(right):
            binary_additivity = binary_additivity and (
                measure(left | right)
                == extended_add(measure(left), measure(right))
            )
            assert not (left == SPACE and right == SPACE)
assert binary_additivity

# Only EMPTY has finite measure. Thus no countable family of finite-measure
# measurable sets can cover the nonempty space.
finite_measure_sets = tuple(
    item for item in SIGMA if isinstance(measure(item), int)
)
assert finite_measure_sets == (EMPTY,)
assert union_all(finite_measure_sets) == EMPTY
assert EMPTY != SPACE
not_sigma_finite = True

# Recompute the null sets and the completed sigma-algebra exactly.
null_sets = frozenset(item for item in SIGMA if measure(item) == 0)
assert null_sets == frozenset((EMPTY,))
subsets_of_space = all_subsets(SPACE)
assert subsets_of_space == SIGMA
completed_sigma = frozenset(
    item for item in subsets_of_space if belongs_to_completion(item)
)
assert completed_sigma == SIGMA

# An extension must agree with measure on every member of SIGMA. Since the
# completion has no additional members, its value on every completed set is
# forced, regardless of what larger exact value space one might allow.
unique_extension = all(item in SIGMA for item in completed_sigma)
assert unique_extension
assert binary_additivity and not_sigma_finite and unique_extension

REPORT = {
    "record_id": "reddit_math_1e744dd",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms the one-point infinite-measure witness: it is a countably additive measure, is not sigma-finite, has only the empty null set, and its completion equals its original power-set sigma-algebra, so every extension to the completion is forced to be the original measure. The refuted necessity statement is substantive, not plainly a typo.",
}

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
