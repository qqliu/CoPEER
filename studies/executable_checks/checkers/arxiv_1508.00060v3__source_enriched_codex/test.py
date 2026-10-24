"""If an input vertex p lies inside the diametral circle on segment ab, then angle apb is less than π/2."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1508.00060v3__source_enriched_codex"
WITNESS_DESCRIPTION = "Take a=(-1,0), b=(1,0), and p=(-1/2,-1/2). The diametral circle has center (0,0) and squared radius 1, while p has squared distance 1/2 from the center, so p lies strictly inside it."
REFUTATION_EXPLANATION = "The vectors a-p=(-1/2,1/2) and b-p=(3/2,1/2) have dot product -1/2. Thus angle apb is obtuse, rather than less than π/2, contradicting the claim."
SEARCH_SPACE = "Fixed a=(-1,0) and b=(1,0); exhaustively tested all 25 points p=(i/2,j/2), where i and j range in fixed order over {-2,-1,0,1,2}, using exact Fraction arithmetic. Strict circle interior was tested by x^2+y^2<1, and the claimed acute angle by (a-p)·(b-p)>0."


def dot(u, v):
    return u[0] * v[0] + u[1] * v[1]


def main():
    a = (Fraction(-1), Fraction(0))
    b = (Fraction(1), Fraction(0))
    numerators = range(-2, 3)
    violations = []

    for i in numerators:
        for j in numerators:
            p = (Fraction(i, 2), Fraction(j, 2))
            strictly_inside = p[0] * p[0] + p[1] * p[1] < Fraction(1)
            ap = (a[0] - p[0], a[1] - p[1])
            bp = (b[0] - p[0], b[1] - p[1])
            acute = dot(ap, bp) > Fraction(0)
            if strictly_inside and not acute:
                violations.append((p, dot(ap, bp)))

    expected = ((Fraction(-1, 2), Fraction(-1, 2)), Fraction(-1, 2))
    assert violations and violations[0] == expected

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
