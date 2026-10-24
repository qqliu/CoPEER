"""Continuity of f and g on X implies the existence of positive radii depending only on ε that work uniformly for every s in X."""

import itertools
import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_12twx2n"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take X = Q with d(x,y)=|x-y|, ε=1, f(x)=x^2, and g(x)=0. "
    "Both functions are continuous on X, but f has no positive radius that "
    "works uniformly in s."
)
REFUTATION_EXPLANATION = (
    "For any σ>0, choose a positive integer n with 1/n<σ, then set s=n and "
    "u=n+1/(2n). Both points lie in Q, |u-s|=1/(2n)<σ, while "
    "|f(u)-f(s)|=(n+1/(2n))^2-n^2=1+1/(4n^2)>1=ε. Hence no positive "
    "uniform radius exists for f, although f and g are continuous."
)
SEARCH_SPACE = (
    "Exhaustively swept all 8 quadratic templates f(x)=a*x^2+b*x+c with "
    "(a,b,c) in {0,1}^3, in itertools.product order, on X=Q with its usual "
    "metric; g(x)=0 and ε=1 were fixed. Each template was tested by an exact "
    "symbolic certificate for the family s=n, u=n+1/(2n). The "
    "lexicographically first certified template was (1,0,0)."
)


def has_uniform_failure_certificate(a, b, c):
    # Put t=1/n.  For u=n+1/(2n) and s=n, cancellation gives
    # f(u)-f(s) = a + (b/2)*t + (a/4)*t^2.
    # The conditions below prove this is greater than epsilon=1 for every t>0.
    del c
    constant = Fraction(a, 1)
    linear = Fraction(b, 2)
    quadratic = Fraction(a, 4)
    return (
        constant >= Fraction(1, 1)
        and linear >= Fraction(0, 1)
        and quadratic > Fraction(0, 1)
    )


def main():
    certified = []
    for coefficients in itertools.product((0, 1), repeat=3):
        if has_uniform_failure_certificate(*coefficients):
            certified.append(coefficients)

    if not certified or certified[0] != (1, 0, 0):
        raise AssertionError("exact bounded search did not find the certificate")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
