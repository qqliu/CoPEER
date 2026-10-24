r"""Drawing an interior diagonal in a (k+1)-sided polygon produces two polygons whose side counts are both between 4 and k."""

import json

RECORD_ID = "reddit_learnmath_157rs31"
VERDICT = "CONFIRMED"
NOTES = ("The refuted statement is substantive as written, not plainly a typo: "
         "exact integer checks show the strictly convex pentagon's interior "
         "diagonal 0-2 creates a triangle and a quadrilateral, with side "
         "counts 3 and 4, so 3 violates the required lower bound 4 (k=4).")


def signed_area_twice(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def boundary_arc(first, last, size):
    arc = [first]
    current = first
    while current != last:
        current = (current + 1) % size
        arc.append(current)
        if len(arc) > size:
            raise RuntimeError("invalid cyclic boundary")
    return tuple(arc)


def require(condition):
    if not condition:
        raise RuntimeError("independent verification failed")


def main():
    k = 4
    polygon = ((0, 0), (2, 0), (3, 1), (2, 3), (0, 2))
    size = len(polygon)
    require(size == k + 1)

    # Every vertex not incident to an oriented boundary edge lies strictly to
    # its left. This exact half-plane test certifies a strictly convex,
    # counterclockwise polygon.
    for edge_start in range(size):
        edge_end = (edge_start + 1) % size
        for vertex_index in range(size):
            if vertex_index != edge_start and vertex_index != edge_end:
                require(signed_area_twice(
                    polygon[edge_start], polygon[edge_end], polygon[vertex_index]
                ) > 0)

    diagonal_start = 0
    diagonal_end = 2
    require(diagonal_end != (diagonal_start + 1) % size)
    require(diagonal_start != (diagonal_end + 1) % size)

    # Its midpoint, represented with coordinates doubled, is strictly inside
    # every boundary half-plane. Convexity then places the open diagonal in
    # the polygon's interior.
    doubled_midpoint = (
        polygon[diagonal_start][0] + polygon[diagonal_end][0],
        polygon[diagonal_start][1] + polygon[diagonal_end][1],
    )
    for edge_start in range(size):
        edge_end = (edge_start + 1) % size
        a = polygon[edge_start]
        b = polygon[edge_end]
        exact_midpoint_side = (
            (b[0] - a[0]) * (doubled_midpoint[1] - 2 * a[1])
            - (b[1] - a[1]) * (doubled_midpoint[0] - 2 * a[0])
        )
        require(exact_midpoint_side > 0)

    first_piece = boundary_arc(diagonal_start, diagonal_end, size)
    second_piece = boundary_arc(diagonal_end, diagonal_start, size)
    side_counts = (len(first_piece), len(second_piece))
    require(first_piece == (0, 1, 2))
    require(second_piece == (2, 3, 4, 0))
    require(side_counts == (3, 4))
    require(not all(4 <= count <= k for count in side_counts))

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
