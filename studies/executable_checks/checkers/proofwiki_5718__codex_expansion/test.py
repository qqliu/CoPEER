"""For every well-ordered set S, the lexicographic order on the set T of all finite tuples over S is not a well-ordering."""

import itertools
import json

RECORD_ID = "proofwiki_5718__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Take S = ∅. It is well-ordered, and its set of finite tuples is T = {()}, whose lexicographic order is a well-order."
REFUTATION_EXPLANATION = "The claim quantifies over every well-ordered set, including the empty set. No positive-length tuple can be formed over S = ∅, so the only finite tuple (including length zero) is (). Every nonempty subset of the singleton T has a least element. Thus T is well-ordered, contradicting the claim. If finite tuples were instead required to have positive length, T would be empty and would still be well-ordered."
SEARCH_SPACE = "The unique carrier set S of cardinality exactly 0, with its unique strict well-order, and its complete set of finite tuples T = {()}; every subset of S and every subset of T was checked exactly."


def all_subsets(items):
    items = tuple(items)
    for mask in range(1 << len(items)):
        yield tuple(items[index] for index in range(len(items)) if mask & (1 << index))


def is_finite_well_order(items, less):
    items = tuple(items)
    for x in items:
        if less(x, x):
            return False
    for x in items:
        for y in items:
            if x != y and (less(x, y) == less(y, x)):
                return False
    for x in items:
        for y in items:
            for z in items:
                if less(x, y) and less(y, z) and not less(x, z):
                    return False
    for subset in all_subsets(items):
        if subset and not any(
            all(candidate == other or less(candidate, other) for other in subset)
            for candidate in subset
        ):
            return False
    return True


def lex_less(left, right, rank):
    for x, y in zip(left, right):
        if x != y:
            return rank[x] < rank[y]
    return len(left) < len(right)


def search():
    candidates = ((),)
    for carrier in candidates:
        rank = {value: index for index, value in enumerate(carrier)}
        carrier_less = lambda x, y: rank[x] < rank[y]
        if not is_finite_well_order(carrier, carrier_less):
            continue

        zero_length_tuples = tuple(itertools.product(carrier, repeat=0))
        positive_length_one = tuple(itertools.product(carrier, repeat=1))
        assert zero_length_tuples == ((),)
        assert positive_length_one == ()
        tuples = zero_length_tuples
        tuple_less = lambda x, y: lex_less(x, y, rank)
        if is_finite_well_order(tuples, tuple_less):
            return carrier, tuples
    return None


witness = search()
assert witness == ((), ((),))
print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, ensure_ascii=True, separators=(",", ":")))
