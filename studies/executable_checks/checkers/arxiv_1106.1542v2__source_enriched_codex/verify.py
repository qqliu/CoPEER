r"""For every sequence of events with P(A_n)→0, divergence of ∑P(A_n) implies P(A_n i.o.)=1."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1106.1542v2__source_enriched_codex"
NOTES = (
    "The witness is valid: for A_n=(0,1/n], exact dyadic-block bounds "
    "prove divergence, while monotonicity and the Archimedean exclusion "
    "argument make the limsup empty. The refuted statement is substantively "
    "false because it lacks a dependence condition; it is not plainly a typo."
)


def measure(n):
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    return Fraction(1, n)


def tail_index(epsilon):
    if not isinstance(epsilon, Fraction) or epsilon <= 0:
        raise ValueError("epsilon must be a positive exact rational")
    n = epsilon.denominator // epsilon.numerator + 1
    assert measure(n) < epsilon
    return n


def dyadic_block_certificate(k):
    if not isinstance(k, int) or k < 0:
        raise ValueError("k must be a nonnegative integer")
    first = 2 ** k
    past_last = 2 ** (k + 1)
    count = past_last - first
    per_term_lower_bound = Fraction(1, past_last)
    structural_lower_bound = count * per_term_lower_bound
    assert structural_lower_bound == Fraction(1, 2)
    exact_block_sum = sum((measure(n) for n in range(first, past_last)), Fraction(0, 1))
    assert exact_block_sum >= structural_lower_bound
    return True


def blocks_exceeding(height):
    if not isinstance(height, Fraction) or height < 0:
        raise ValueError("height must be a nonnegative exact rational")
    blocks = 2 * (height.numerator // height.denominator + 1)
    certified_lower_bound = Fraction(blocks, 2)
    assert certified_lower_bound > height
    return blocks


def exclusion_index(x):
    if not isinstance(x, Fraction) or x <= 0 or x > 1:
        raise ValueError("x must represent a point of (0,1]")
    n = x.denominator // x.numerator + 1
    assert Fraction(1, n) < x
    return n


vanishing = all(
    measure(tail_index(epsilon)) < epsilon
    for epsilon in (
        Fraction(1, 2),
        Fraction(1, 19),
        Fraction(7, 1000),
        Fraction(1, 1000000),
    )
)

# Every dyadic block has sum at least 1/2, and an exact number of blocks can
# therefore be constructed whose certified partial-sum lower bound exceeds
# any prescribed rational height.
divergence = all(dyadic_block_certificate(k) for k in range(13)) and all(
    Fraction(blocks_exceeding(height), 2) > height
    for height in (
        Fraction(0, 1),
        Fraction(5, 3),
        Fraction(20, 1),
        Fraction(1001, 7),
    )
)

# The endpoints 1/n strictly decrease. For each x>0, the Archimedean choice
# n>1/x gives 1/n<x, and all later endpoints are smaller still. Thus every
# point is eventually outside the events, so their decreasing limsup is empty.
decreasing = all(measure(n + 1) < measure(n) for n in range(1, 100))
empty_limsup = decreasing and all(
    measure(exclusion_index(x)) < x
    for x in (
        Fraction(1, 1),
        Fraction(2, 3),
        Fraction(1, 97),
        Fraction(113, 1000000),
    )
)

verdict = "CONFIRMED" if vanishing and divergence and empty_limsup else "CANNOT_REPRODUCE"
print(json.dumps({"record_id": RECORD_ID, "verdict": verdict, "notes": NOTES}, ensure_ascii=False))
