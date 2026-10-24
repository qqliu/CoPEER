r"""The rewrite x=b(a/b+√2) is valid for arbitrary rational coefficients a and b."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_learnmath_o5qbvs",
    "verdict": "CONFIRMED",
    "notes": "For the exact rational witness a=-1 and b=0, the quotient a/b is undefined, so the proposed right-hand side is undefined. This is a substantive missing-domain-condition error, not a plain typo.",
}


def rational_quotient_is_defined(divisor):
    assert isinstance(divisor, Fraction)
    return divisor.numerator != 0


def verify():
    a = Fraction(-1, 1)
    b = Fraction(0, 1)

    assert a.numerator == -1 and a.denominator == 1
    assert b.numerator == 0 and b.denominator == 1

    witness_is_rational = isinstance(a, Fraction) and isinstance(b, Fraction)
    quotient_is_defined = rational_quotient_is_defined(b)
    rewritten_expression_is_defined = quotient_is_defined

    assert witness_is_rational
    assert not quotient_is_defined
    assert not rewritten_expression_is_defined
    assert REPORT["verdict"] == "CONFIRMED"


verify()
print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
