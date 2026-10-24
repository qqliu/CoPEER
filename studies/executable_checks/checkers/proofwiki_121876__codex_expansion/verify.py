"""The assumed commutative topological semigroup has an identity element 0_G."""

import json

RECORD_ID = "proofwiki_121876__codex_expansion"
CONFIRMED_NOTES = (
    "The refuted statement is substantive, not plainly a typo: the constant "
    "operation on the two-point discrete space is an associative, commutative, "
    "continuous binary operation with no identity element."
)


def power_set(items):
    subsets = (frozenset(),)
    for item in items:
        singleton = frozenset((item,))
        subsets = subsets + tuple(part | singleton for part in subsets)
    return frozenset(subsets)


def operation(left, right, carrier):
    if left not in carrier or right not in carrier:
        raise ValueError("operand outside carrier")
    return 0


def main():
    carrier = frozenset((0, 1))
    points = tuple(carrier)
    discrete_topology = power_set(points)

    product_points = frozenset(
        (left, right) for left in carrier for right in carrier
    )
    discrete_product_topology = power_set(tuple(product_points))

    closed = all(
        operation(left, right, carrier) in carrier
        for left in carrier
        for right in carrier
    )
    associative = all(
        operation(operation(x, y, carrier), z, carrier)
        == operation(x, operation(y, z, carrier), carrier)
        for x in carrier
        for y in carrier
        for z in carrier
    )
    commutative = all(
        operation(x, y, carrier) == operation(y, x, carrier)
        for x in carrier
        for y in carrier
    )

    continuous = True
    for open_set in discrete_topology:
        preimage = frozenset(
            pair
            for pair in product_points
            if operation(pair[0], pair[1], carrier) in open_set
        )
        if preimage not in discrete_product_topology:
            continuous = False

    identities = tuple(
        candidate
        for candidate in carrier
        if all(
            operation(candidate, element, carrier) == element
            and operation(element, candidate, carrier) == element
            for element in carrier
        )
    )

    established = (
        closed
        and associative
        and commutative
        and continuous
        and not identities
    )
    if established:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = (
            "The proposed substantive counterexample did not pass the exact "
            "finite verification."
        )

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }))


if __name__ == "__main__":
    main()
