r"""If a finite group has a set factorization G=BC and at least one of B or C is a subgroup, then G=CB."""

import json

RECORD_ID = "arxiv_2006.06396v2__source_enriched_codex"
CONFIRMED_NOTES = "Exact recomputation in S3 confirms B is a subgroup, BC=S3, and CB has only four elements; the refuted statement is substantive, not plainly a typo."
INVALID_NOTES = "Independent exact recomputation did not validate the concrete witness; the purported refutation is therefore invalid."


def compose(left, right):
    return tuple(left[right[position]] for position in range(3))


def cycle(entries):
    result = list(range(3))
    for position in range(len(entries)):
        result[entries[position]] = entries[(position + 1) % len(entries)]
    return tuple(result)


def product(first, second):
    return frozenset(compose(x, y) for x in first for y in second)


def subgroup(candidate, group, identity):
    if not candidate.issubset(group) or identity not in candidate:
        return False
    if any(compose(x, y) not in candidate for x in candidate for y in candidate):
        return False
    return all(
        any(compose(x, y) == identity and compose(y, x) == identity for y in candidate)
        for x in candidate
    )


def main():
    points = range(3)
    group = frozenset(
        (a, b, c)
        for a in points
        for b in points
        for c in points
        if a != b and a != c and b != c
    )
    identity = tuple(points)

    group_is_valid = (
        len(group) == 6
        and all(compose(x, y) in group for x in group for y in group)
        and all(compose(identity, x) == x and compose(x, identity) == x for x in group)
        and all(
            compose(compose(x, y), z) == compose(x, compose(y, z))
            for x in group
            for y in group
            for z in group
        )
        and all(
            any(compose(x, y) == identity and compose(y, x) == identity for y in group)
            for x in group
        )
    )

    swap_01 = cycle((0, 1))
    swap_02 = cycle((0, 2))
    rotate_012 = cycle((0, 1, 2))
    set_b = frozenset((identity, swap_01))
    set_c = frozenset((identity, swap_02, rotate_012))

    bc = product(set_b, set_c)
    cb = product(set_c, set_b)
    reported_cb = frozenset((identity, swap_01, swap_02, rotate_012))

    verified = (
        group_is_valid
        and subgroup(set_b, group, identity)
        and bc == group
        and cb == reported_cb
        and cb != group
        and len(cb) == 4
    )

    result = {
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID",
        "notes": CONFIRMED_NOTES if verified else INVALID_NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
