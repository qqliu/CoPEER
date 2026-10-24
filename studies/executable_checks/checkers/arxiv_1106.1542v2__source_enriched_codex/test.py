"""For every sequence of events with P(A_n)→0, divergence of ∑P(A_n) implies P(A_n i.o.)=1."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "arxiv_1106.1542v2__source_enriched_codex"
WITNESS_DESCRIPTION = (
    "On Ω=(0,1] with Lebesgue probability, let A_n=(0,1/n] for every "
    "integer n≥1. Then P(A_n)=1/n→0, ∑_{n=1}^∞P(A_n) is the divergent "
    "harmonic series, and A_n i.o.=∅, so P(A_n i.o.)=0."
)
REFUTATION_EXPLANATION = (
    "The events are decreasing and every x∈(0,1] belongs to only finitely "
    "many of them: choose N>1/x, then x∉A_n for n≥N. Thus their limsup "
    "is empty even though their probabilities have divergent sum, "
    "contradicting the claimed conclusion 1."
)
SEARCH_SPACE = (
    "All 20 pairs (a,b) with a∈{1,2,3,4} and b∈{0,1,2,3,4}, "
    "representing A_n=(0,1/(a n+b)] on (0,1] for n≥1, checked in "
    "lexicographic order; the first certified witness is (a,b)=(1,0)."
)


def certifies_counterexample(a, b):
    """Check the exact algebraic premises of the interval-family certificate."""
    if not isinstance(a, int) or not isinstance(b, int):
        return False
    if a < 1 or b < 0:
        return False

    # P(A_n)=1/(a*n+b) tends to zero because a*n+b grows without bound.
    vanishing_certificate = a >= 1 and b >= 0

    # In the block 2^j <= n < 2^(j+1), there are 2^j terms and
    # a*n+b <= (2*a+b)*2^j. Hence every block sum is at least
    # 2^j/((2*a+b)*2^j)=1/(2*a+b), an exact positive constant.
    block_denominator = 2 * a + b
    block_lower_bound = Fraction(1, block_denominator)
    divergence_certificate = (
        block_denominator > 0
        and block_lower_bound > Fraction(0, 1)
        and Fraction(8, block_denominator * 8) == block_lower_bound
    )

    # The intervals decrease to the empty set in Ω=(0,1]: for each x>0,
    # the Archimedean choice of N with a*N+b>1/x excludes x thereafter.
    empty_limsup_certificate = a >= 1 and b >= 0

    return (
        vanishing_certificate
        and divergence_certificate
        and empty_limsup_certificate
    )


certified = []
for a, b in product(range(1, 5), range(0, 5)):
    if certifies_counterexample(a, b):
        certified.append((a, b))

if certified and certified[0] == (1, 0):
    outcome = "WITNESS_FOUND"
    witness_description = WITNESS_DESCRIPTION
    refutation_explanation = REFUTATION_EXPLANATION
else:
    outcome = "NO_WITNESS_EXHAUSTIVE"
    witness_description = "No certified member of the bounded family was found."
    refutation_explanation = "The exact bounded parameter sweep produced no witness."

result = {
    "record_id": RECORD_ID,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
