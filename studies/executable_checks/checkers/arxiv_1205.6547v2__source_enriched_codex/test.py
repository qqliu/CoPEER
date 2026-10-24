"""For integers n≥0 and 0≤k≤n, the displayed integral of the kth derivative of e^{-x^2} against G_n(x) equals the stated finite sum."""

import json
from fractions import Fraction
from math import factorial

RECORD_ID = "arxiv_1205.6547v2__source_enriched_codex"
BOUND = 12
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be certified from the supplied quote."
REFUTATION_EXPLANATION = (
    "The quote does not define G_n(x), the scalar symbols G_j in the finite "
    "sum, or conditions ensuring or evaluating the improper integral. "
    "Consequently neither side can be computed from n and k alone, so the "
    "bounded exact sweep cannot decide equality or inequality."
)
SEARCH_SPACE = (
    "All 91 integer pairs (n,k) with 0≤n≤12 and 0≤k≤n, and for each pair "
    "every even summation index l with 0≤l≤n-k; exact rational coefficients "
    "were constructed in lexicographic (n,k,l) order. This is an illustrative "
    "bounded sweep, not an exhaustive test of the universal claim."
)


def stated_terms(n, k):
    terms = []
    for ell in range(0, n - k + 1, 2):
        denominator = (
            (2 ** k)
            * factorial(k)
            * factorial(n - k - ell)
            * (2 ** ell)
            * factorial(ell // 2)
        )
        coefficient = Fraction(factorial(n), denominator)
        terms.append((n - k - ell, coefficient))
    return tuple(terms)


def sweep(bound):
    cases = []
    for n in range(bound + 1):
        for k in range(n + 1):
            terms = stated_terms(n, k)
            cases.append((n, k, terms, None))
    return tuple(cases)


def main():
    cases = sweep(BOUND)
    expected_case_count = (BOUND + 1) * (BOUND + 2) // 2
    assert len(cases) == expected_case_count == 91
    assert all(status is None for _, _, _, status in cases)
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
