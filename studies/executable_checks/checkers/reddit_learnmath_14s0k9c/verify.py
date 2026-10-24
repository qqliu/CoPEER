r"""Under an embedding into a symmetric group, every element of order 2 must map to a single transposition."""

import json

RECORD = "reddit_learnmath_14s0k9c"
CONFIRMED_NOTES = "Exact recomputation verifies that (1 2)(3 4) has order 2, gives an injective homomorphism C2 into S4, and is not a single transposition. The refuted statement is substantive, not plainly a typo."
INVALID_NOTES = "The reported witness did not pass exact verification. The intended refutation is substantive, not plainly a typo."


def permutation_product(left, right):
    result = []
    for point in range(4):
        result.append(left[right[point]])
    return tuple(result)


def main():
    identity = tuple(range(4))
    witness_list = list(identity)
    for first, second in ((0, 1), (2, 3)):
        witness_list[first], witness_list[second] = witness_list[second], witness_list[first]
    witness = tuple(witness_list)

    is_permutation = tuple(sorted(witness)) == identity
    has_order_two = witness != identity and permutation_product(witness, witness) == identity

    images = {0: identity, 1: witness}
    homomorphism = True
    for left in (0, 1):
        for right in (0, 1):
            product_in_c2 = (left + right) % 2
            if permutation_product(images[left], images[right]) != images[product_in_c2]:
                homomorphism = False
    injective = images[0] != images[1]

    moved_points = []
    for point in range(4):
        if witness[point] != point:
            moved_points.append(point)
    is_single_transposition = len(moved_points) == 2

    valid = (
        is_permutation
        and has_order_two
        and homomorphism
        and injective
        and not is_single_transposition
    )
    verdict = "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID"
    notes = CONFIRMED_NOTES if valid else INVALID_NOTES
    print(json.dumps({"record_id": RECORD, "verdict": verdict, "notes": notes}, separators=(",", ":")))


if __name__ == "__main__":
    main()
