r"""Lemma 1. A non-empty face F of a polyhedron is minimal if and only if F is a single point (i.e., dim(F) = 0)."""

import json

REPORT = {
    "record_id": "Algorithms_47__sol3",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: for P = R, the whole line is a face and its only non-empty face, yet it contains 0 and 1 and has affine dimension 1. The refuted statement is substantive, not a typo; it overlooks polyhedra with lineality.",
}


def add_forms(left, right):
    assert len(left) == len(right)
    return tuple(left[index] + right[index] for index in range(len(left)))


def subtract_forms(left, right):
    assert len(left) == len(right)
    return tuple(left[index] - right[index] for index in range(len(left)))


def scale_form(integer, form):
    assert isinstance(integer, int)
    return tuple(integer * coefficient for coefficient in form)


# An empty H-presentation in one ambient dimension denotes the entire real
# line. The candidate face has the same presentation, so it is P itself.
ambient_dimension = 1
polyhedron_inequalities = ()
face_inequalities = ()
assert ambient_dimension == 1
assert len(polyhedron_inequalities) == 0
assert face_inequalities == polyhedron_inequalities

# Every convex set is a face of itself: endpoints already in P are necessarily
# in F when F and P have identical membership conditions. The empty system is
# convex, since every real number satisfies it.
assert all(coefficient == 0 and bound == 0
           for coefficient, bound in polyhedron_inequalities)
assert face_inequalities == polyhedron_inequalities

# Exact symbolic minimality certificate. Forms are coefficients of arbitrary
# real variables (z, y). Given z in a non-empty face and arbitrary y in R, put
# u = 2z-y. Then u+y=2z, so z is the strict midpoint of u and y when y differs
# from z. The defining face property therefore puts y in the face. If y=z it
# is already there. Thus every non-empty face of R is all of R.
z_form = (1, 0)
y_form = (0, 1)
u_form = subtract_forms(scale_form(2, z_form), y_form)
midpoint_identity = add_forms(u_form, y_form) == scale_form(2, z_form)
endpoint_difference = subtract_forms(u_form, y_form)
expected_difference = scale_form(2, subtract_forms(z_form, y_form))
assert midpoint_identity
assert endpoint_difference == expected_difference
assert 2 != 0
assert 0 < 1 < 2
minimal_nonempty_face = midpoint_identity and endpoint_difference == expected_difference
assert minimal_nonempty_face

# Two distinct exact points of F certify affine dimension one in a
# one-dimensional ambient space.
first_point = 0
second_point = 1
assert first_point != second_point
assert all(coefficient * first_point <= bound
           for coefficient, bound in face_inequalities)
assert all(coefficient * second_point <= bound
           for coefficient, bound in face_inequalities)
affine_dimension = 1 if second_point - first_point != 0 else 0
assert affine_dimension == 1
assert minimal_nonempty_face and affine_dimension != 0

print(json.dumps(REPORT, separators=(",", ":")))
