"""If a finite group has a set factorization G=BC and at least one of B or C is a subgroup, then G=CB."""

import itertools
import json

RECORD_ID = "arxiv_2006.06396v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "In S3, using (p q)(i)=p(q(i)), take B={(),(01)} and C={(),(02),(012)}. Then B is a subgroup, BC=S3, but CB={(),(01),(02),(012)}."
REFUTATION_EXPLANATION = "Direct multiplication gives BC={(),(01),(02),(12),(012),(021)}=S3, whereas CB omits (12) and (021). Thus G=BC with B a subgroup does not imply G=CB."
SEARCH_SPACE = "All 4,096 ordered pairs (B,C) of subsets of S3 were swept in increasing subset-bitmask order; each pair was tested for BC=S3, whether B or C is a subgroup, and whether CB differs from S3."

ELEMENTS = tuple(itertools.permutations(range(3)))
IDENTITY = (0, 1, 2)
WHOLE_GROUP = frozenset(ELEMENTS)


def multiply(p, q):
    """Return p after q, so (p q)(i) = p(q(i))."""
    return tuple(p[q[i]] for i in range(3))


def inverse(p):
    result = [0, 0, 0]
    for i in range(3):
        result[p[i]] = i
    return tuple(result)


def subset_from_mask(mask):
    return frozenset(
        ELEMENTS[index]
        for index in range(len(ELEMENTS))
        if mask & (1 << index)
    )


def set_product(left, right):
    result = set()
    for x in left:
        for y in right:
            result.add(multiply(x, y))
    return frozenset(result)


def is_subgroup(candidate):
    if IDENTITY not in candidate:
        return False
    for x in candidate:
        if inverse(x) not in candidate:
            return False
        for y in candidate:
            if multiply(x, y) not in candidate:
                return False
    return True


def main():
    chosen_b = frozenset({IDENTITY, (1, 0, 2)})
    chosen_c = frozenset({IDENTITY, (2, 1, 0), (1, 2, 0)})
    chosen_found = False
    counterexample_count = 0

    limit = 1 << len(ELEMENTS)
    for b_mask in range(limit):
        b = subset_from_mask(b_mask)
        b_is_subgroup = is_subgroup(b)
        for c_mask in range(limit):
            c = subset_from_mask(c_mask)
            bc = set_product(b, c)
            c_is_subgroup = is_subgroup(c)
            violates = (
                bc == WHOLE_GROUP
                and (b_is_subgroup or c_is_subgroup)
                and set_product(c, b) != WHOLE_GROUP
            )
            if violates:
                counterexample_count += 1
                if b == chosen_b and c == chosen_c:
                    chosen_found = True

    assert counterexample_count > 0
    assert chosen_found
    assert is_subgroup(chosen_b)
    assert set_product(chosen_b, chosen_c) == WHOLE_GROUP
    assert set_product(chosen_c, chosen_b) == frozenset(
        {IDENTITY, (1, 0, 2), (2, 1, 0), (1, 2, 0)}
    )

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
