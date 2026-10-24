r"""For every nonconstant polynomial F in \mathbb{Z}[x_1,\ldots,x_r] and every prime p, the number c_p(F) of zeros of F modulo p satisfies c_p(F) \leq \deg(F)p^{r-1}."""

import itertools
import json

RECORD_ID = "arxiv_2207.06033v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take r=1, p=2, and F(x_1)=2x_1. Both residues 0 and 1 are zeros "
    "modulo 2, so c_2(F)=2."
)
REFUTATION_EXPLANATION = (
    "The polynomial F is nonconstant over the integers and has degree 1, "
    "but c_2(F)=2 while deg(F) p^(r-1)=1*2^0=1. Thus 2>1, "
    "contradicting the claimed universal bound."
)
SEARCH_SPACE = (
    "Exhaustively swept all 1,860 pairs with r=1, p in (2,3,5), degree d "
    "in (1,2,3), and coefficient tuple (a_0,...,a_d) in "
    "(0,1,-1,2,-2)^(d+1) with a_d nonzero; every residue x_1 in range(p) "
    "was tested. The first violation in this fixed order was retained."
)


def evaluate_mod(coefficients, x, p):
    value = 0
    for coefficient in reversed(coefficients):
        value = (value * x + coefficient) % p
    return value


def main():
    coefficient_values = (0, 1, -1, 2, -2)
    primes = (2, 3, 5)
    degrees = (1, 2, 3)
    first_violation = None
    pairs_checked = 0

    for p in primes:
        for degree in degrees:
            for coefficients in itertools.product(
                coefficient_values, repeat=degree + 1
            ):
                if coefficients[-1] == 0:
                    continue
                pairs_checked += 1
                zero_count = sum(
                    1
                    for x in range(p)
                    if evaluate_mod(coefficients, x, p) == 0
                )
                bound = degree * p ** 0
                if zero_count > bound and first_violation is None:
                    first_violation = (p, degree, coefficients, zero_count, bound)

    assert pairs_checked == 1860
    assert first_violation == (2, 1, (0, 2), 2, 1)

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
