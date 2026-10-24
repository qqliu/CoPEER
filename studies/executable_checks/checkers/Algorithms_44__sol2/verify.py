r"""|hP(v) -hP(w)| = max x in P (v * x) - max z in P (w * z) <= max x in P |(v -w) * x| <= Mv -w."""

import json

REPORT = {
    "record_id": "Algorithms_44__sol2",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms the witness: for P={1}, v=0, and w=1, the absolute support-function difference is 1 while the directed difference is -1. The refuted equality is plainly a typo—an absolute value is missing around the directed difference—not a substantive failure of the usual Lipschitz bound.",
}


def support(points, direction):
    point_iterator = iter(points)
    first_point = next(point_iterator)
    greatest = direction * first_point
    for point in point_iterator:
        candidate = direction * point
        if candidate > greatest:
            greatest = candidate
    return greatest


points = (1,)
v = 0
w = 1
h_v = support(points, v)
h_w = support(points, w)
absolute_difference = abs(h_v - h_w)
directed_difference = h_v - h_w
maximum_absolute_product = support(tuple(abs((v - w) * x) for x in points), 1)

assert h_v == 0
assert h_w == 1
assert absolute_difference == 1
assert directed_difference == -1
assert maximum_absolute_product == 1
assert absolute_difference <= maximum_absolute_product
assert absolute_difference != directed_difference

print(json.dumps(REPORT, separators=(",", ":")))
