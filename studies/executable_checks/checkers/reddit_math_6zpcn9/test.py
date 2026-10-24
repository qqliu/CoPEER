"""If a_n/b_n tends to 0 and the series of b_n converges, then the series of a_n converges."""

from fractions import Fraction
import json

RECORD_ID = "reddit_math_6zpcn9"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "For n >= 0, let b_n = (-1)^n/(n+1), let H_m = sum_{j=1}^m 1/j, "
    "and let a_n = 1/((n+1)H_{n+1})."
)
REFUTATION_EXPLANATION = (
    "The series of b_n converges by the alternating-series test. Also a_n/b_n = "
    "(-1)^n/H_{n+1}, which tends to 0 because H_m tends to infinity. However, "
    "the series of a_n diverges: for every k >= 1, the terms with 2^(k-1) < m "
    "<= 2^k have H_m <= k+1 and m <= 2^k, so their sum is at least "
    "1/(2(k+1)); these block lower bounds have a divergent sum. Thus the "
    "hypotheses hold while the series of a_n does not converge."
)
SEARCH_SPACE = (
    "All 8 shifted harmonic templates c in {1,2,3,4,5,6,7,8}, with "
    "b_n = (-1)^n/(n+c) and a_n = 1/((n+c)H_{n+c}), were enumerated "
    "in fixed increasing order. The generic exact proof applies to every "
    "positive c; the reported witness is c=1. The sweep is exhaustive only "
    "over this explicitly finite template family, not over all sequences."
)


def harmonic(m):
    total = Fraction(0, 1)
    for j in range(1, m + 1):
        total += Fraction(1, j)
    return total


def reciprocal(value):
    if value == 0:
        raise ZeroDivisionError("reciprocal of zero")
    return Fraction(value.denominator, value.numerator)


def b_value(c, n):
    return Fraction((-1) ** n, n + c)


def a_value(c, n):
    h = harmonic(n + c)
    return Fraction(1, n + c) * reciprocal(h)


def template_has_generic_proof(c):
    # For positive c, b is an alternating tail with decreasing magnitudes.
    # The ratio is exactly (-1)^n/H_(n+c), and deleting a finite prefix does
    # not affect either H_m tending to infinity or divergence of sum 1/(m H_m).
    return isinstance(c, int) and c >= 1


candidates = tuple(range(1, 9))
certified = []
for c in candidates:
    if template_has_generic_proof(c):
        certified.append(c)

# The bounded template search visits and certifies every candidate.
assert tuple(certified) == candidates
chosen_c = certified[0]
assert chosen_c == 1

# Exact finite sanity checks of the displayed identities. These checks are not
# used as substitutes for the generic infinite arguments stated above.
for n in range(33):
    h = harmonic(n + chosen_c)
    ratio = a_value(chosen_c, n) * reciprocal(b_value(chosen_c, n))
    expected = Fraction(((-1) ** n) * h.denominator, h.numerator)
    assert ratio == expected

# Exact instances of the dyadic inequalities used in the divergence proof.
for k in range(1, 9):
    endpoint = 2 ** k
    assert harmonic(endpoint) <= Fraction(k + 1, 1)
    assert harmonic(endpoint) >= Fraction(2 + k, 2)
    block_total = Fraction(0, 1)
    first = (2 ** (k - 1)) + 1
    for m in range(first, endpoint + 1):
        block_total += a_value(1, m - 1)
    assert block_total >= Fraction(1, 2 * (k + 1))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False, separators=(",", ":")))
