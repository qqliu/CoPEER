"""From f(0)=1 and f(x+1)=f(x)+1 for every real x, induction implies f(x)=x+1 for every real x."""

import json
from fractions import Fraction

RECORD_ID = "reddit_askmath_1dlgmq7"
VERDICT = "CONFIRMED"
NOTES = "The witness is valid. The refuted statement is substantive, not a typo: integer induction only propagates values within each coset of the integers."


def witness_function(q):
    if q.denominator == 1:
        return q + Fraction(1, 1)
    return q + Fraction(2, 1)


def shift_affine(form, amount):
    coefficient, constant = form
    return coefficient, constant + coefficient * amount


def add_constant(form, amount):
    coefficient, constant = form
    return coefficient, constant + amount


def main():
    zero = Fraction(0, 1)
    one = Fraction(1, 1)
    half = Fraction(1, 2)

    # Translation by 1 preserves membership in the integers in both directions:
    # closure proves x in Z => x+1 in Z, and subtracting 1 proves the converse.
    integer_translations = (one, -one)
    assert all(step.denominator == 1 for step in integer_translations)

    # On either invariant branch the function is the affine form x+k.
    # Verify symbolically and exactly that f(x+1)=f(x)+1 for every x in it.
    for branch_constant in (one, Fraction(2, 1)):
        branch_form = (one, branch_constant)
        assert shift_affine(branch_form, one) == add_constant(branch_form, one)

    assert witness_function(zero) == one
    actual = witness_function(half)
    claimed = half + one
    assert actual == Fraction(5, 2)
    assert claimed == Fraction(3, 2)
    assert actual != claimed

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
