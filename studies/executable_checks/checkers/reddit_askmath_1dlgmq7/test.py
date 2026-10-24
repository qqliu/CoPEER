"""From f(0)=1 and f(x+1)=f(x)+1 for every real x, induction implies f(x)=x+1 for every real x."""

import json
from fractions import Fraction
from itertools import product


def candidate_value(offset, x):
    """Evaluate the rational restriction of the stated real-valued candidate."""
    if x.denominator == 1:
        return x + 1
    return x + 1 + offset


def main():
    offsets = (
        Fraction(1, 1),
        Fraction(-1, 1),
        Fraction(2, 1),
        Fraction(-2, 1),
    )
    points = (
        Fraction(1, 2),
        Fraction(-1, 2),
        Fraction(3, 2),
        Fraction(-3, 2),
    )

    violations = []
    for offset, x in product(offsets, points):
        assert candidate_value(offset, Fraction(0, 1)) == 1
        if candidate_value(offset, x) != x + 1:
            violations.append((offset, x))

    assert len(violations) == len(offsets) * len(points)
    assert violations[0] == (Fraction(1, 1), Fraction(1, 2))

    result = {
        "record_id": "reddit_askmath_1dlgmq7",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Let f(x)=x+1 when x is an integer and f(x)=x+2 otherwise. Then x=1/2 is a witness: f(1/2)=5/2, whereas x+1=3/2.",
        "refutation_explanation": "This f has f(0)=1. For every real x, x is an integer if and only if x+1 is an integer, so both branches give f(x+1)=f(x)+1. Nevertheless f(1/2) is not 1/2+1. Induction only determines values along each coset x+Z, not across all real numbers.",
        "search_space": "The program exhaustively sweeps the 16-element Cartesian product c in {1,-1,2,-2} and x in {1/2,-1/2,3/2,-3/2}, in the displayed fixed order, for the candidate functions f_c(x)=x+1 on integers and f_c(x)=x+1+c otherwise. The first violation is (c,x)=(1,1/2).",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
