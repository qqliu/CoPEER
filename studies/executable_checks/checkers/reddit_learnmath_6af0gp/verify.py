r'''For every point a of a compact subspace A of a Hausdorff space X, there is an open neighborhood U_a such that U_a ∩ A = {a}.'''

import json

RECORD_ID = "reddit_learnmath_6af0gp"
VERDICT = "CONFIRMED"
NOTES = ("The witness is valid. The refuted statement is substantive, not "
         "plainly a typo: compact Hausdorff subspaces need not be discrete, "
         "and 0 is a non-isolated limit point of A.")


def reciprocal_less_than(n, numerator, denominator):
    # All quantities are positive, so 1/n < numerator/denominator is
    # equivalent to denominator < numerator*n.
    return denominator < numerator * n


def tail_start(numerator, denominator):
    # For every positive rational radius numerator/denominator, this constructs
    # an index whose reciprocal is strictly inside that radius.
    assert isinstance(numerator, int) and numerator > 0
    assert isinstance(denominator, int) and denominator > 0
    quotient, remainder = divmod(denominator, numerator)
    assert denominator == quotient * numerator + remainder
    assert 0 <= remainder < numerator
    n = quotient + 1
    assert reciprocal_less_than(n, numerator, denominator)
    return n


def verify_witness():
    # Represent 1/n exactly by the integer pair (1, n). The first exact terms
    # confirm positivity, distinctness, and strict descent without approximation.
    terms = tuple((1, n) for n in range(1, 257))
    assert all(numerator == 1 and denominator > 0
               for numerator, denominator in terms)
    assert len(set(terms)) == len(terms)
    assert all(terms[index][1] < terms[index + 1][1]
               for index in range(len(terms) - 1))

    # Exercise the universal integer construction on exact rational radii.
    for numerator in range(1, 65):
        for denominator in range(1, 129):
            n = tail_start(numerator, denominator)
            assert n > 0
            assert reciprocal_less_than(n, numerator, denominator)

    # In the usual real topology, every neighborhood of 0 contains an interval
    # about 0 and hence one with a positive rational radius. tail_start then
    # supplies a nonzero point 1/n of A in that neighborhood, so 0 is not
    # isolated. The same tail bound leaves only finitely many sequence points
    # outside the cover member containing 0; selecting one cover member for
    # each remaining point proves A compact. The real line is Hausdorff.
    assert tail_start(1, 1) == 2


def main():
    verify_witness()
    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
