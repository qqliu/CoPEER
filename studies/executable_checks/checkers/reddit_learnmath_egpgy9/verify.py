r"""A quadrilateral with all four sides equal must be a square."""

import json

record_id = "reddit_learnmath_egpgy9"
verdict = "CONFIRMED"
notes = "The statement is substantively false, not plainly a typo: exact integer calculations verify a strictly convex equal-sided quadrilateral with a non-right interior angle."

vertices = ((-2, 0), (0, -1), (2, 0), (0, 1))
assert len(set(vertices)) == 4

edges = []
for index in range(4):
    start = vertices[index]
    end = vertices[(index + 1) % 4]
    edges.append((end[0] - start[0], end[1] - start[1]))

side_squares = [x * x + y * y for x, y in edges]
assert side_squares == [5, 5, 5, 5]

turns = []
for index in range(4):
    first = edges[index]
    second = edges[(index + 1) % 4]
    turns.append(first[0] * second[1] - first[1] * second[0])
assert turns == [4, 4, 4, 4]

ray_to_next = (
    vertices[1][0] - vertices[0][0],
    vertices[1][1] - vertices[0][1],
)
ray_to_previous = (
    vertices[3][0] - vertices[0][0],
    vertices[3][1] - vertices[0][1],
)
first_angle_dot = (
    ray_to_next[0] * ray_to_previous[0]
    + ray_to_next[1] * ray_to_previous[1]
)
assert first_angle_dot == 3
assert first_angle_dot != 0

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
