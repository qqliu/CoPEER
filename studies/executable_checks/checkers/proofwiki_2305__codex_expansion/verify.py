r"""For every ordered integral domain D, the map g: Z → D defined by g(n)=n·1_D is onto D."""

import json
from fractions import Fraction

record_id = "proofwiki_2305__codex_expansion"
confirmed_notes = "Independently confirmed using exact rational arithmetic: Q with its usual order is an ordered integral domain, and 1/2 is not g(n) for any integer n because 2n=1 has no integer solution. The refuted statement is substantive, not plainly a typo; the source quote only asserts an embedding into D, not surjectivity."
invalid_notes = "The proposed witness could not be independently established. The statement would be substantive rather than plainly a typo."

one = Fraction(1, 1)
witness = Fraction(1, 2)
zero = Fraction(0, 1)

# In Q, g(n) is exactly n/1. Equality n/1 = 1/2 would require
# 2*n = 1. Every multiple of 2 has residue zero modulo 2, whereas 1 does not.
def g(n):
    if type(n) is not int:
        raise TypeError("g is defined on integers")
    return Fraction(n, 1) * one

rational_construction_valid = (
    one != zero
    and witness > zero
    and witness < one
    and witness.numerator == 1
    and witness.denominator == 2
    and g(0) == zero
    and g(1) == one
)
integer_equation_impossible = (2 % 2 == 0) and (1 % 2 != 0)
confirmed = rational_construction_valid and integer_equation_impossible

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if confirmed else invalid_notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
