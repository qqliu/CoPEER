r"""Four spheres in three dimensions have at most two common intersection points, with two possible when their centers are coplanar."""

import json

record_id = "reddit_askmath_1c1k74p"
centers = ((0, 0, -1), (0, 0, 0), (0, 0, 1), (0, 0, 2))
radius_squares = (2, 1, 2, 5)
points = ((-1, 0, 0), (0, -1, 0), (0, 1, 0), (1, 0, 0))

def distance_square(point, center):
    total = 0
    for index in range(3):
        difference = point[index] - center[index]
        total += difference * difference
    return total

sphere_data = tuple(zip(centers, radius_squares))
distinct_spheres = len(set(sphere_data)) == 4
positive_radius_squares = all(value > 0 for value in radius_squares)
distinct_points = len(set(points)) == 4
all_incident = all(
    distance_square(point, center) == radius_square
    for point in points
    for center, radius_square in sphere_data
)
coplanar_centers = all(center[0] == 0 for center in centers)
verified = (
    distinct_spheres
    and positive_radius_squares
    and distinct_points
    and len(points) > 2
    and all_incident
    and coplanar_centers
)

if verified:
    verdict = "CONFIRMED"
    notes = "Exact integer arithmetic verifies that the four spheres are distinct and that all four distinct reported points lie on every sphere; four common points contradict the asserted maximum of two. The refuted statement is substantive, not plainly a typo: it omits a nondegeneracy condition, and these coplanar (indeed collinear) centers produce a common circle."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The exact witness checks failed; the substantive statement was not refuted by the reported points."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
