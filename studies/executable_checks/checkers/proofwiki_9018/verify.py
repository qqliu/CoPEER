r"""The closing claim that the same proof works for a general ring, with or without unity. The proof's construction explicitly uses the sequences <1,0,0,...> and x = <0,1,0,...>, which require a multiplicative identity 1 in R; in a ring without unity these elements do not exist and the key computation x^2 = <0,0,1,0,...> can fail outright."""

import json

RECORD_ID = "proofwiki_9018"
CONFIRMED_NOTES = "The witness is valid: {0,2} under modulo-4 operations is a nonunital ring, and exact convolution gives (0,2,0,0)^2 = (0,0,0,0), not (0,0,2,0). The refuted statement is substantive, not plainly a typo."
INVALID_NOTES = "The independently checked witness did not establish the claimed failure. The refuted statement would be substantive, not plainly a typo."
R = (0, 2)


def plus(a, b):
    return (a + b) % 4


def times(a, b):
    return (a * b) % 4


def ring_checks():
    closure = all(
        plus(a, b) in R and times(a, b) in R
        for a in R
        for b in R
    )
    additive_identity = all(plus(0, a) == a and plus(a, 0) == a for a in R)
    additive_inverses = all(
        any(plus(a, b) == 0 and plus(b, a) == 0 for b in R)
        for a in R
    )
    additive_commutativity = all(plus(a, b) == plus(b, a) for a in R for b in R)
    additive_associativity = all(
        plus(plus(a, b), c) == plus(a, plus(b, c))
        for a in R
        for b in R
        for c in R
    )
    multiplicative_associativity = all(
        times(times(a, b), c) == times(a, times(b, c))
        for a in R
        for b in R
        for c in R
    )
    distributivity = all(
        times(a, plus(b, c)) == plus(times(a, b), times(a, c))
        and times(plus(a, b), c) == plus(times(a, c), times(b, c))
        for a in R
        for b in R
        for c in R
    )
    return all((
        closure,
        additive_identity,
        additive_inverses,
        additive_commutativity,
        additive_associativity,
        multiplicative_associativity,
        distributivity,
    ))


def has_multiplicative_identity():
    return any(
        all(times(candidate, a) == a and times(a, candidate) == a for a in R)
        for candidate in R
    )


def product_prefix(left, right):
    coefficients = []
    for degree in range(len(left)):
        total = 0
        for left_degree in range(len(left)):
            right_degree = degree - left_degree
            if 0 <= right_degree < len(right):
                total = plus(total, times(left[left_degree], right[right_degree]))
        coefficients.append(total)
    return tuple(coefficients)


def main():
    x = (0, 2, 0, 0)
    square = product_prefix(x, x)
    valid = (
        ring_checks()
        and not has_multiplicative_identity()
        and 1 not in R
        and times(2, 2) == 0
        and square == (0, 0, 0, 0)
        and square != (0, 0, 2, 0)
    )
    result = {
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID",
        "notes": CONFIRMED_NOTES if valid else INVALID_NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
