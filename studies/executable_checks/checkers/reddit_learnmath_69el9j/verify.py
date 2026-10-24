r"""The stated two cases—having an angle greater than 90 degrees or having all angles less than 90 degrees—exhaust all triangles."""

import json

record_id = "reddit_learnmath_69el9j"
first_angle = 1
second_angle = 89
triangle_angle_sum = 180
right_angle = 90
third_angle = triangle_angle_sum - first_angle - second_angle
angles = (first_angle, second_angle, third_angle)

is_triangle_angle_triple = (
    all(angle > 0 for angle in angles)
    and all(angle < triangle_angle_sum for angle in angles)
    and sum(angles) == triangle_angle_sum
)
has_obtuse_angle = any(angle > right_angle for angle in angles)
has_only_acute_angles = all(angle < right_angle for angle in angles)
outside_both_cases = not has_obtuse_angle and not has_only_acute_angles
matches_reported_witness = angles == (1, 89, 90)

confirmed = (
    matches_reported_witness
    and is_triangle_angle_triple
    and outside_both_cases
)

verdict = "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID"
notes = (
    "Exact recomputation confirms that (1, 89, 90) is a valid triangle-angle "
    "triple and belongs to neither stated case. The refuted exhaustion statement "
    "is substantive because it omits all right triangles; it is not plainly a typo."
    if confirmed
    else
    "Exact recomputation does not validate the reported witness. The refuted "
    "statement would be substantive rather than plainly a typo."
)

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":"), ensure_ascii=False))
