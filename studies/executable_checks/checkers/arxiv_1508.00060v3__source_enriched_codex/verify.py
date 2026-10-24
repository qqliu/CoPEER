"""If an input vertex p lies inside the diametral circle on segment ab, then angle apb is less than π/2."""

import json
from fractions import Fraction

record_id = "arxiv_1508.00060v3__source_enriched_codex"
verdict = "CONFIRMED"
notes = "Exact recomputation confirms that p is strictly inside the diametral circle and that (a-p)·(b-p) = -1/2, so angle apb is obtuse and the stated claim fails. The refuted statement is plainly a reversed-inequality typo: an interior point gives an angle greater than π/2."

a = (Fraction(-1, 1), Fraction(0, 1))
b = (Fraction(1, 1), Fraction(0, 1))
p = (Fraction(-1, 2), Fraction(-1, 2))

center = (
    (a[0] + b[0]) * Fraction(1, 2),
    (a[1] + b[1]) * Fraction(1, 2),
)
radius_vector = (a[0] - center[0], a[1] - center[1])
point_vector = (p[0] - center[0], p[1] - center[1])
radius_squared = radius_vector[0] * radius_vector[0] + radius_vector[1] * radius_vector[1]
distance_squared = point_vector[0] * point_vector[0] + point_vector[1] * point_vector[1]

vector_to_a = (a[0] - p[0], a[1] - p[1])
vector_to_b = (b[0] - p[0], b[1] - p[1])
dot_product = vector_to_a[0] * vector_to_b[0] + vector_to_a[1] * vector_to_b[1]

if not distance_squared < radius_squared:
    raise AssertionError("the proposed point is not strictly inside the circle")
if vector_to_a == (Fraction(0, 1), Fraction(0, 1)) or vector_to_b == (Fraction(0, 1), Fraction(0, 1)):
    raise AssertionError("the angle is degenerate")
if dot_product != Fraction(-1, 2) or not dot_product < Fraction(0, 1):
    raise AssertionError("the proposed angle is not obtuse")

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False))
