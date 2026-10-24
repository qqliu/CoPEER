r"""Every element τ of Gal(F/K) fixes F pointwise."""

import json

RECORD_ID = "proofwiki_11907__codex_expansion"
CONFIRMED_NOTES = (
    "Exact finite-field recomputation validates the witness: GF(4) is a field, "
    "tau is its nonidentity GF(2)-fixing automorphism, and tau(a)=1+a. "
    "The refuted statement is plainly an F-for-K typo; elements of Gal(F/K) "
    "fix K pointwise, not generally F."
)
INVALID_NOTES = "The supplied witness did not pass exact finite-field verification."
ELEMENTS = tuple(range(4))
BASE_FIELD = (0, 1)
TAU = (0, 1, 3, 2)


def add(left, right):
    return left ^ right


def product(left, right):
    polynomial = 0
    multiplicand = left
    multiplier = right
    while multiplier:
        if multiplier & 1:
            polynomial ^= multiplicand
        multiplicand <<= 1
        multiplier >>= 1

    # Reduce modulo X^2 + X + 1, represented by the bits 111.
    for degree in range(polynomial.bit_length() - 1, 1, -1):
        if polynomial & (1 << degree):
            polynomial ^= 7 << (degree - 2)
    return polynomial


def field_is_valid():
    if 0 == 1:
        return False
    for x in ELEMENTS:
        if add(x, 0) != x or product(x, 1) != x or product(x, 0) != 0:
            return False
        if not any(add(x, y) == 0 for y in ELEMENTS):
            return False
        if x != 0 and not any(product(x, y) == 1 for y in ELEMENTS):
            return False
        for y in ELEMENTS:
            if add(x, y) not in ELEMENTS or product(x, y) not in ELEMENTS:
                return False
            if add(x, y) != add(y, x) or product(x, y) != product(y, x):
                return False
            for z in ELEMENTS:
                if add(add(x, y), z) != add(x, add(y, z)):
                    return False
                if product(product(x, y), z) != product(x, product(y, z)):
                    return False
                if product(x, add(y, z)) != add(product(x, y), product(x, z)):
                    return False
    return True


def witness_is_valid():
    if not field_is_valid():
        return False
    if any(add(x, y) not in BASE_FIELD or product(x, y) not in BASE_FIELD
           for x in BASE_FIELD for y in BASE_FIELD):
        return False
    if tuple(sorted(TAU)) != ELEMENTS:
        return False
    if any(TAU[x] != x for x in BASE_FIELD):
        return False
    if any(TAU[x] != product(x, x) for x in ELEMENTS):
        return False
    for x in ELEMENTS:
        for y in ELEMENTS:
            if TAU[add(x, y)] != add(TAU[x], TAU[y]):
                return False
            if TAU[product(x, y)] != product(TAU[x], TAU[y]):
                return False
    return TAU[2] == 3 and TAU[2] != 2


def main():
    valid = witness_is_valid()
    result = {
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID",
        "notes": CONFIRMED_NOTES if valid else INVALID_NOTES,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
