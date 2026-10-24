"""A homotopy changing winding number from n to zero must cross the origin exactly n times as an unsigned event count."""

import itertools
import json
from fractions import Fraction

RECORD_ID = "reddit_math_1jh0y7o"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take n=1 and H(t,theta)=(cos(theta)+a(t), sin(theta)), where a(t) is "
    "piecewise linear through a(0)=0, a(1/3)=2, a(2/3)=0, and a(1)=2. "
    "The loop meets the origin at exactly t=1/6, 1/2, and 5/6, once at each time."
)
REFUTATION_EXPLANATION = (
    "The initial loop is the unit circle and has winding number 1 about the origin. "
    "The final loop is the unit circle translated two units to the right and has "
    "winding number zero. Every origin event is transverse, but their unsigned count "
    "is 3, not n=1, so the claimed exact count is false."
)
SEARCH_SPACE = (
    "All four piecewise-linear center paths having knot times 0, 1/3, 2/3, 1, "
    "endpoint values 0 and 2, and each of the two intermediate values in {0,2}. "
    "The program sweeps all four in fixed itertools.product order and computes every "
    "crossing time exactly with Fraction arithmetic."
)


def crossing_times(center_knots):
    """Return times when the translated unit circle contains the origin."""
    result = []
    segment_count = len(center_knots) - 1
    for index in range(segment_count):
        left = center_knots[index]
        right = center_knots[index + 1]
        crosses_one = (left < 1 < right) or (right < 1 < left)
        if crosses_one:
            start_time = Fraction(index, segment_count)
            segment_length = Fraction(1, segment_count)
            interpolation = Fraction(1 - left, right - left)
            result.append(start_time + segment_length * interpolation)
    return tuple(result)


candidate_space = tuple(
    (0,) + middle + (2,)
    for middle in itertools.product((0, 2), repeat=2)
)
assert len(candidate_space) == 4

witnesses = []
for candidate in candidate_space:
    events = crossing_times(candidate)
    # Center 0 gives winding number 1; center 2 gives winding number 0.
    if len(events) != 1:
        witnesses.append((candidate, events))

assert witnesses == [
    ((0, 2, 0, 2), (Fraction(1, 6), Fraction(1, 2), Fraction(5, 6)))
]

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, separators=(",", ":")))
