"""Four spheres in three dimensions have at most two common intersection points, with two possible when their centers are coplanar."""

import json
from itertools import product

RECORD_ID = "reddit_askmath_1c1k74p"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Four distinct spheres with (center, squared radius) equal to ((0,0,-1),2), ((0,0,0),1), ((0,0,1),2), and ((0,0,2),5) have the four common points (-1,0,0), (0,-1,0), (0,1,0), and (1,0,0)."
REFUTATION_EXPLANATION = "For every listed point, the squared distances to the four centers are respectively 2, 1, 2, and 5, so all four points lie on all four spheres. Thus the spheres have at least four common intersection points, contradicting the claimed maximum of two. Their centers are collinear and therefore coplanar."
SEARCH_SPACE = "The program exhaustively checks the single ordered quadruple of four distinct spheres with centers (0,0,-1), (0,0,0), (0,0,1), (0,0,2) and squared radii 2, 1, 2, 5 against all 27 integer points in {-1,0,1}^3."

spheres = (
    ((0, 0, -1), 2),
    ((0, 0, 0), 1),
    ((0, 0, 1), 2),
    ((0, 0, 2), 5),
)

common_points = []
for point in product(range(-1, 2), repeat=3):
    lies_on_all = True
    for center, radius_squared in spheres:
        distance_squared = sum(
            (coordinate - center_coordinate) ** 2
            for coordinate, center_coordinate in zip(point, center)
        )
        if distance_squared != radius_squared:
            lies_on_all = False
            break
    if lies_on_all:
        common_points.append(point)

expected_points = [(-1, 0, 0), (0, -1, 0), (0, 1, 0), (1, 0, 0)]
assert common_points == expected_points

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, separators=(",", ":")))
