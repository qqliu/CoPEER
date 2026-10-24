r"""There exists exactly one sequence of diagonal neighborhoods satisfying V_0 = V, symmetry of V_n for every n > 0, and V_n \circ V_n \subseteq V_{n-1} for every n > 0."""

import json

record_id = "proofwiki_116857__codex_expansion"
confirmed_notes = (
    "Exact finite-set recomputation confirms two distinct sequences on the "
    "two-point discrete space: the constant positive tails Delta and X x X "
    "are diagonal neighborhoods, symmetric, and square to themselves, so "
    "every required inclusion holds. The refuted uniqueness statement is "
    "substantive, not plainly a typo."
)

points = (0, 1)
pairs = tuple((left, right) for left in points for right in points)
diagonal = frozenset((value, value) for value in points)
universal = frozenset(pairs)

# Since the topology is discrete, its open sets are exactly all subsets.
open_sets = tuple(
    frozenset(
        pair for index, pair in enumerate(pairs) if mask & (1 << index)
    )
    for mask in range(1 << len(pairs))
)


def is_diagonal_neighborhood(relation):
    return any(
        diagonal.issubset(open_set) and open_set.issubset(relation)
        for open_set in open_sets
    )


def transpose(relation):
    return frozenset((right, left) for left, right in relation)


def compose(relation):
    return frozenset(
        (left, right)
        for left in points
        for right in points
        if any(
            (left, middle) in relation and (middle, right) in relation
            for middle in points
        )
    )


def validates_constant_positive_tail(tail):
    square = compose(tail)
    # At n = 1 the predecessor is universal; at every n >= 2 it is tail.
    return (
        is_diagonal_neighborhood(universal)
        and is_diagonal_neighborhood(tail)
        and tail == transpose(tail)
        and square.issubset(universal)
        and square.issubset(tail)
    )


first_sequence_valid = validates_constant_positive_tail(diagonal)
second_sequence_valid = validates_constant_positive_tail(universal)
sequences_are_distinct = diagonal != universal
squares_recomputed_exactly = (
    compose(diagonal) == diagonal and compose(universal) == universal
)
confirmed = (
    first_sequence_valid
    and second_sequence_valid
    and sequences_are_distinct
    and squares_recomputed_exactly
)

if confirmed:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = (
        "Exact finite-set recomputation did not validate both proposed "
        "sequences, so the reported witness is invalid."
    )

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}))
