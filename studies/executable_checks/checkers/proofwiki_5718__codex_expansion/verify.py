r"""For every well-ordered set S, the lexicographic order on the set T of all finite tuples over S is not a well-ordering."""

import json

RECORD_ID = "proofwiki_5718__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = ("Exact independent recomputation confirms the witness: the empty set is "
         "well-ordered, its finite-tuple set is the singleton containing the empty "
         "tuple, and the induced lexicographic order is a well-order. The refuted "
         "statement is substantive, not plainly a typo: its universal quantifier "
         "omits a necessary restriction on the size of S.")


def subsets(values):
    values = tuple(values)
    if not values:
        return ((),)
    tail_subsets = subsets(values[1:])
    without_first = tuple(part for part in tail_subsets)
    with_first = tuple((values[0],) + part for part in tail_subsets)
    return without_first + with_first


def is_strict_well_order(values, before):
    values = tuple(values)
    if any(before(value, value) for value in values):
        return False
    for left in values:
        for right in values:
            if left != right:
                if before(left, right) == before(right, left):
                    return False
    for first in values:
        for second in values:
            for third in values:
                if before(first, second) and before(second, third):
                    if not before(first, third):
                        return False
    for part in subsets(values):
        if part:
            least_exists = False
            for candidate in part:
                if all(candidate == other or before(candidate, other)
                       for other in part):
                    least_exists = True
            if not least_exists:
                return False
    return True


def lexicographically_before(left, right, element_before):
    shared_length = min(len(left), len(right))
    for index in range(shared_length):
        if left[index] != right[index]:
            return element_before(left[index], right[index])
    return len(left) < len(right)


carrier = ()
carrier_before = lambda left, right: False

# There is one tuple of length zero. A positive-length tuple over an empty
# carrier cannot exist because its first component would have to be in carrier.
finite_tuples = ((),)
tuple_before = lambda left, right: lexicographically_before(
    left, right, carrier_before
)

carrier_verified = is_strict_well_order(carrier, carrier_before)
tuple_set_complete = (
    len(carrier) == 0
    and finite_tuples == ((),)
    and all(len(sequence) == 0 for sequence in finite_tuples)
)
tuple_order_verified = is_strict_well_order(finite_tuples, tuple_before)

if not (carrier_verified and tuple_set_complete and tuple_order_verified):
    raise AssertionError("exact witness verification failed")

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}, separators=(",", ":")))
