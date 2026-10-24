"""Let k and l be integers with k,l≥3. From an arrangement of k tropical anti-hyperplanes, form the usual affine arrangement with hyperplanes H_{i,j} given by x_j=v_{i,j} for j∈{1,…,l−1} and by ∑_{j'=1}^{l−1}x_{j'}=v_{i,l} for j=l, and homogenize it by adjoining the hyperplane at infinity. Normalize the parameters by v_{0,j}=v_{i,0}=0. Consider the hyperplane arrangement in the remaining parameter space whose defining linear functionals are the non-identically-zero determinants of the l-tuples specified in the source. Let N be the number of those l-tuples,
N:=k^l+2·binom(k,2)·binom(l,2)·k^{l−2}+l·k^{l−1}=(k+l+(k−1)binom(l,2))k^{l−1},
and let R be the rank of this determinant-hyperplane arrangement; the construction gives R≤(k−1)(l−1). The claim is that
2^R N^{R−1}/(R−1)! ≤ N^{R−1}."""

import json
from fractions import Fraction
from math import comb, factorial

RECORD_ID = "arxiv_math_0312069v3__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS = (
    "Take k=3 and l=3. Then N=108, while the nonzero defining functionals "
    "imply 1≤R≤(k−1)(l−1)=4. Every possible rank R∈{1,2,3,4} violates "
    "the claimed inequality."
)
EXPLANATION = (
    "Because N=108>0, division by N^(R−1) reduces the claim to "
    "2^R/(R−1)!≤1. For R=1,2,3,4, the exact left-hand ratios are "
    "respectively 2, 4, 4, and 8/3, all strictly greater than 1. Thus the "
    "inequality fails regardless of the arrangement's exact rank for k=l=3."
)
SEARCH_SPACE = (
    "Exhaustive sweep over k∈{3}, l∈{3}, and every positive integer rank "
    "allowed by R≤(k−1)(l−1): R∈{1,2,3,4}. Four exact-arithmetic cases "
    "were checked."
)

violations = []
for k in range(3, 4):
    for l in range(3, 4):
        n = (
            k ** l
            + 2 * comb(k, 2) * comb(l, 2) * k ** (l - 2)
            + l * k ** (l - 1)
        )
        rank_bound = (k - 1) * (l - 1)
        for rank in range(1, rank_bound + 1):
            power = n ** (rank - 1)
            left = Fraction((2 ** rank) * power, factorial(rank - 1))
            right = Fraction(power, 1)
            if left > right:
                violations.append((k, l, n, rank, Fraction(2 ** rank, factorial(rank - 1))))

expected = [
    (3, 3, 108, 1, Fraction(2, 1)),
    (3, 3, 108, 2, Fraction(4, 1)),
    (3, 3, 108, 3, Fraction(4, 1)),
    (3, 3, 108, 4, Fraction(8, 3)),
]
assert violations == expected

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS,
    "refutation_explanation": EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False))
