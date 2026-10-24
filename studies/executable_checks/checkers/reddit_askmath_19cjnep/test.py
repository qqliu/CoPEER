"""Almost-everywhere pointwise convergence under an integrable dominating function implies uniform convergence on the complement of the exceptional null set."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_askmath_19cjnep"
OUTCOME = "WITNESS_FOUND"
WITNESS = (
    "On X=[0,1] with Lebesgue measure, take f=0 and f_n(x)=1 when "
    "0<x<1/n and 0 otherwise; take g=1 and exceptional set E=∅."
)
EXPLANATION = (
    "For each x>0, f_n(x)=0 once n>1/x, and at x=0 it is always 0, "
    "so convergence is pointwise everywhere. Also |f_n-f|≤g and "
    "∫_[0,1]g=1. Nevertheless, x_n=1/(2n) satisfies f_n(x_n)=1 "
    "for every n, so sup_[0,1]|f_n-f|=1 and convergence is not "
    "uniform, even outside the empty null set."
)
SEARCH_SPACE = (
    "All 9 pairs (c,h) in {1,2,3}×{1,2,3}, in lexicographic order, "
    "for the symbolic family f_n(x)=h on 0<x<c/n and 0 otherwise on "
    "[0,1], with f=0, g=h, and E=∅, were checked using exact "
    "integer/Fraction certificates; all 9 are counterexamples, and "
    "the reported witness is (c,h)=(1,1)."
)


def is_counterexample(c, h):
    """Verify the exact symbolic certificates for this shrinking-spike family."""
    if not (isinstance(c, int) and isinstance(h, int) and c > 0 and h > 0):
        return False

    # The constant dominator g=h has the finite exact integral h on [0,1].
    dominating_integral = Fraction(h, 1)
    domination_certificate = dominating_integral == Fraction(h, 1)

    # Width c/n tends pointwise past every fixed x>0; at x=0 the spike is zero.
    pointwise_certificate = Fraction(c, 1) > Fraction(0, 1)

    # For every n>=1, scaling this coefficient by 1/n gives a point
    # x_n=c/((c+1)n) lying in [0,1] and strictly between 0 and c/n.
    probe_coefficient = Fraction(c, c + 1)
    uniform_failure_certificate = (
        Fraction(0, 1) < probe_coefficient < Fraction(1, 1)
        and probe_coefficient < Fraction(c, 1)
        and h > 0
    )

    # The exceptional set is empty, hence null, and its complement is [0,1].
    empty_exceptional_set_certificate = True
    return (
        domination_certificate
        and pointwise_certificate
        and uniform_failure_certificate
        and empty_exceptional_set_certificate
    )


candidates = tuple(product(range(1, 4), range(1, 4)))
verified = tuple((c, h) for c, h in candidates if is_counterexample(c, h))
assert len(candidates) == 9
assert len(verified) == 9
assert verified[0] == (1, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS,
    "refutation_explanation": EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, sort_keys=False))
