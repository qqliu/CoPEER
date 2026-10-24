r'''A homotopy changing winding number from n to zero must cross the origin exactly n times as an unsigned event count.'''

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_math_1jh0y7o",
    "verdict": "CONFIRMED",
    "notes": "Exact rational recomputation gives three distinct transverse origin events at t=1/6, 1/2, and 5/6, while the endpoint winding numbers are 1 and 0. This is a substantive refutation, not a typo: winding constrains a signed intersection count, not the unsigned event count.",
}

# Independently specified witness data: knot times and horizontal circle centers.
knot_times = (Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(1))
centers = (0, 2, 0, 2)

# On each nonconstant affine segment, solve a(t)=1 exactly.  The translated
# unit circle contains the origin precisely then: its required source point is
# (u,v)=(-a(t),0), and u*u+v*v=1 is equivalent here to a(t)*a(t)=1.
events = []
slopes = []
for position in range(3):
    time_left = knot_times[position]
    time_right = knot_times[position + 1]
    center_left = centers[position]
    center_right = centers[position + 1]
    low = min(center_left, center_right)
    high = max(center_left, center_right)
    if low < 1 < high:
        fraction_along = Fraction(1 - center_left, center_right - center_left)
        event_time = time_left + (time_right - time_left) * fraction_along
        events.append(event_time)
        duration = time_right - time_left
        slope = Fraction(
            (center_right - center_left) * duration.denominator,
            duration.numerator,
        )
        slopes.append(slope)

assert tuple(events) == (Fraction(1, 6), Fraction(1, 2), Fraction(5, 6))
assert len(set(events)) == 3
assert all(knot_times[0] < event < knot_times[-1] for event in events)
assert tuple(slopes) == (Fraction(6), Fraction(-6), Fraction(6))
assert all(slope != 0 for slope in slopes)

# At every event a=1, so (-1,0) is the unique point of the source unit circle
# translated to the origin.  The nonzero center slope makes the two-dimensional
# homotopy map transverse there (its Jacobian determinant is minus that slope).
for event, slope in zip(events, slopes):
    center_at_event = Fraction(1)
    source_u = -center_at_event
    source_v = Fraction(0)
    assert source_u * source_u + source_v * source_v == 1
    assert source_u + center_at_event == 0
    assert source_v == 0
    assert -slope != 0

# Compute endpoint winding numbers by signed crossings of the positive x-axis.
# For the counterclockwise circle centered at c, theta=0 contributes +1 when
# c+1>0, while theta=pi contributes -1 when c-1>0.  Neither endpoint circle
# passes through the origin, so this exact ray-crossing computation is valid.
def endpoint_winding(center):
    assert center * center != 1
    total = 0
    if center + 1 > 0:
        total += 1
    if center - 1 > 0:
        total -= 1
    return total

initial_winding = endpoint_winding(centers[0])
final_winding = endpoint_winding(centers[-1])
assert initial_winding == 1
assert final_winding == 0
assert len(events) == 3
assert len(events) != initial_winding

print(json.dumps(REPORT, separators=(",", ":")))
