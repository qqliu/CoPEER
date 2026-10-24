"""Sigma-finiteness is necessary to ensure uniqueness of the measure extension to the completion."""

import json
from itertools import combinations

ZERO = (False, 0)
ONE = (False, 1)
INFINITY = (True, 0)


def add_values(left, right):
    if left[0] or right[0]:
        return INFINITY
    return (False, left[1] + right[1])


def powerset(elements):
    ordered = tuple(sorted(elements))
    return tuple(
        frozenset(choice)
        for size in range(len(ordered) + 1)
        for choice in combinations(ordered, size)
    )


def is_measure(algebra, measure):
    empty = frozenset()
    if measure[empty] != ZERO:
        return False
    for left in algebra:
        for right in algebra:
            if left.isdisjoint(right):
                if measure[left | right] != add_values(measure[left], measure[right]):
                    return False
    return True


def is_sigma_finite(space, algebra, measure):
    covered = frozenset()
    for measurable_set in algebra:
        if not measure[measurable_set][0]:
            covered = covered | measurable_set
    return covered == space


def completion(algebra, measure):
    completed = set()
    for measurable_set in algebra:
        for null_set in algebra:
            if measure[null_set] == ZERO:
                for null_subset in powerset(null_set):
                    completed.add(measurable_set | null_subset)
    return frozenset(completed)


def main():
    space = frozenset((0,))
    algebra = powerset(space)
    algebra_as_set = frozenset(algebra)
    candidate_values = (ZERO, ONE, INFINITY)
    witnesses = []
    swept = 0

    for singleton_value in candidate_values:
        swept += 1
        measure = {
            frozenset(): ZERO,
            space: singleton_value,
        }
        valid = is_measure(algebra, measure)
        sigma_finite = is_sigma_finite(space, algebra, measure)
        completed_algebra = completion(algebra, measure)
        extension_is_unique = completed_algebra == algebra_as_set
        if valid and not sigma_finite and extension_is_unique:
            witnesses.append(singleton_value)

    if swept != 3 or witnesses != [INFINITY]:
        raise RuntimeError("deterministic exhaustive search produced an unexpected result")

    result = {
        "record_id": "reddit_math_1e744dd",
        "outcome": "WITNESS_FOUND",
        "witness_description": "X={0}, Σ=P(X), μ(∅)=0, and μ({0})=∞.",
        "refutation_explanation": "This is a measure but is not σ-finite: its only finite-measure measurable set is ∅, which cannot cover X. Its only null set is ∅, so it is already complete; its completion has the same σ-algebra P(X). Therefore an extension to the completion is forced to equal μ on every set and is unique despite failure of σ-finiteness.",
        "search_space": "Exactly all three assignments μ(∅)=0 and μ({0})∈{0,1,∞} on the one-point set X={0} with σ-algebra P(X), in the fixed order 0, 1, ∞.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
