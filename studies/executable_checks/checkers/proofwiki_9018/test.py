"""The closing claim that the same proof works for a general ring, with or without unity. The proof's construction explicitly uses the sequences <1,0,0,...> and x = <0,1,0,...>, which require a multiplicative identity 1 in R; in a ring without unity these elements do not exist and the key computation x^2 = <0,0,1,0,...> can fail outright."""

import json


RECORD_ID = "proofwiki_9018"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "R = {0,2} with addition and multiplication modulo 4 is a ring without "
    "unity. Its only nonzero element satisfies 2*2 = 0, so the degree-one "
    "sequence (0,2,0,0) squares to (0,0,0,0), not to the corresponding "
    "shifted sequence (0,0,2,0)."
)
REFUTATION_EXPLANATION = (
    "Exhaustive axiom checks verify that R is a ring and that neither of its "
    "elements is a multiplicative identity. Consequently the proof's "
    "required coefficient 1 and the sequence (0,1,0,...) do not exist in R. "
    "The explicit convolution calculation also exhibits the stated failure, "
    "so this same construction does not work for this ring without unity."
)
SEARCH_SPACE = (
    "All 8 subsets of {0,1,2,3} containing 0, with addition and "
    "multiplication inherited modulo 4; every subset was checked exhaustively "
    "for the ring axioms and for the existence of a multiplicative identity."
)


def add(a, b):
    return (a + b) % 4


def mul(a, b):
    return (a * b) % 4


def is_ring(elements):
    if 0 not in elements:
        return False

    for a in elements:
        if not any(add(a, b) == 0 and add(b, a) == 0 for b in elements):
            return False
        for b in elements:
            if add(a, b) not in elements or mul(a, b) not in elements:
                return False
            if add(a, b) != add(b, a):
                return False
            for c in elements:
                if add(add(a, b), c) != add(a, add(b, c)):
                    return False
                if mul(mul(a, b), c) != mul(a, mul(b, c)):
                    return False
                if mul(a, add(b, c)) != add(mul(a, b), mul(a, c)):
                    return False
                if mul(add(a, b), c) != add(mul(a, c), mul(b, c)):
                    return False
    return True


def has_unity(elements):
    return any(
        all(mul(e, a) == a and mul(a, e) == a for a in elements)
        for e in elements
    )


def convolution(left, right):
    length = len(left)
    output = []
    for degree in range(length):
        coefficient = 0
        for index in range(degree + 1):
            coefficient = add(
                coefficient,
                mul(left[index], right[degree - index]),
            )
        output.append(coefficient)
    return tuple(output)


def main():
    nonunital_rings = []
    checked_subsets = 0

    for mask in range(16):
        elements = tuple(value for value in range(4) if mask & (1 << value))
        if 0 not in elements:
            continue
        checked_subsets += 1
        if is_ring(elements) and not has_unity(elements):
            nonunital_rings.append(elements)

    witness = (0, 2)
    degree_one = (0, 2, 0, 0)

    assert checked_subsets == 8
    assert witness in nonunital_rings
    assert is_ring(witness)
    assert not has_unity(witness)
    assert 1 not in witness
    assert convolution(degree_one, degree_one) == (0, 0, 0, 0)
    assert convolution(degree_one, degree_one) != (0, 0, 2, 0)

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
