r"""Lemma 1. A non-empty face F of a polyhedron is minimal if and only if F is a single point (i.e., dim(F) = 0)."""

import json

REPORT = {
    "record_id": "Algorithms_47__sol3",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take P = R in ambient dimension 1 and F = P. The face F is non-empty and minimal, but it contains the distinct points 0 and 1, so it is not a single point and has dimension 1.",
    "refutation_explanation": "The whole polyhedron F = P is a face because it is the equality set of the valid inequality 0*x <= 0. It is minimal among non-empty faces: if G is any non-empty face of R and z is in G, then for every y != z, z is the midpoint of y and 2*z-y; the face property forces both endpoints, including y, into G. Thus G = R. Since F contains 0 and 1, this minimal non-empty face is not a point, contradicting the forward implication.",
    "search_space": "The finite search space was exactly the singleton consisting of ambient dimension 1, the H-polyhedron P defined by the empty tuple of inequalities (so P = R), and the candidate whole face F exposed by 0*x <= 0; distinctness and positive dimension were certified by the ordered pair (0, 1).",
}


def satisfies(inequalities, point):
    return all(coefficient * point <= bound
               for coefficient, bound in inequalities)


def valid_on_unconstrained_line(coefficient, bound):
    # coefficient*x <= bound holds for every real x exactly in this case.
    return coefficient == 0 and 0 <= bound


def equality_is_whole_unconstrained_line(coefficient, bound):
    return coefficient == 0 and bound == 0


def minimality_certificate_for_whole_line():
    # For symbolic variables z and y, set x = 2*z-y.  In the ordered
    # coefficient basis (z, y), x+y = 2*z.  Hence z is the midpoint of
    # x and y.  Also x-y = 2*(z-y), so when y differs from z the two
    # endpoints differ.  A non-empty face containing z must therefore
    # contain arbitrary y, proving that it is the whole line.
    x_coefficients = (2, -1)
    y_coefficients = (0, 1)
    x_plus_y = (
        x_coefficients[0] + y_coefficients[0],
        x_coefficients[1] + y_coefficients[1],
    )
    twice_z = (2, 0)
    x_minus_y = (
        x_coefficients[0] - y_coefficients[0],
        x_coefficients[1] - y_coefficients[1],
    )
    twice_z_minus_y = (2, -2)
    return x_plus_y == twice_z and x_minus_y == twice_z_minus_y


# (ambient dimension, H-inequalities, exposing coefficient, exposing bound,
#  first certified point, second certified point)
CANDIDATES = (
    (1, (), 0, 0, 0, 1),
)

found = None
for candidate in CANDIDATES:
    ambient_dimension, inequalities, face_coefficient, face_bound, p, q = candidate
    if ambient_dimension != 1:
        continue
    if inequalities != ():
        continue
    if not satisfies(inequalities, p) or not satisfies(inequalities, q):
        continue
    if p == q:
        continue
    if not valid_on_unconstrained_line(face_coefficient, face_bound):
        continue
    if not equality_is_whole_unconstrained_line(face_coefficient, face_bound):
        continue
    if not minimality_certificate_for_whole_line():
        continue
    face_dimension = 1
    if face_dimension == 0:
        continue
    found = candidate
    break

if found is None:
    raise AssertionError("the exhaustive singleton search found no witness")
if REPORT["record_id"] != "Algorithms_47__sol3":
    raise AssertionError("report record mismatch")
if REPORT["outcome"] != "WITNESS_FOUND":
    raise AssertionError("report outcome mismatch")
if "P = R" not in REPORT["witness_description"]:
    raise AssertionError("report does not name the searched witness")
if "(0, 1)" not in REPORT["search_space"]:
    raise AssertionError("report omits the exact distinct-point certificate")

print(json.dumps(REPORT, separators=(",", ":")))
