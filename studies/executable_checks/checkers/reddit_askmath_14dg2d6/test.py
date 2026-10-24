"""Negating yaw, pitch, and roll while retaining their original composition order gives the inverse rotation used to transform vector coordinates."""

import json
from itertools import product


def matmul(a, b):
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )


def transpose(a):
    return tuple(tuple(a[j][i] for j in range(3)) for i in range(3))


def apply(a, v):
    return tuple(sum(a[i][j] * v[j] for j in range(3)) for i in range(3))


def rotation(axis, quarter_turns):
    c, s = ((1, 0), (0, 1), (-1, 0), (0, -1))[quarter_turns % 4]
    if axis == "x":
        return ((1, 0, 0), (0, c, -s), (0, s, c))
    if axis == "y":
        return ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def compose(yaw, pitch, roll):
    return matmul(
        matmul(rotation("z", yaw), rotation("y", pitch)),
        rotation("x", roll),
    )


first_witness = None
checked = 0
for yaw, pitch, roll in product(range(4), repeat=3):
    original = compose(yaw, pitch, roll)
    same_order_negation = compose(-yaw, -pitch, -roll)
    true_inverse = transpose(original)
    checked += 1
    if same_order_negation != true_inverse and first_witness is None:
        first_witness = (yaw, pitch, roll, same_order_negation, true_inverse)

assert checked == 64
assert first_witness is not None
yaw, pitch, roll, same_order_negation, true_inverse = first_witness
assert (yaw, pitch, roll) == (0, 1, 1)
assert apply(same_order_negation, (1, 0, 0)) == (0, 0, 1)
assert apply(true_inverse, (1, 0, 0)) == (0, 1, 0)

result = {
    "record_id": "reddit_askmath_14dg2d6",
    "outcome": "WITNESS_FOUND",
    "witness_description": "yaw = 0°, pitch = 90°, roll = 90° with right-handed column-vector rotations Rz(yaw)Ry(pitch)Rx(roll).",
    "refutation_explanation": "Negating while retaining that order sends (1,0,0) to (0,0,1), whereas the true inverse Rx(-90)Ry(-90)Rz(0) sends it to (0,1,0). Therefore the rotations are unequal.",
    "search_space": "All 64 triples (yaw, pitch, roll) in {0°, 90°, 180°, 270°}^3 were checked using exact integer matrices, with yaw about z, pitch about y, roll about x, and original product Rz(yaw)Ry(pitch)Rx(roll), in lexicographic quarter-turn order.",
}
print(json.dumps(result, separators=(",", ":")))
