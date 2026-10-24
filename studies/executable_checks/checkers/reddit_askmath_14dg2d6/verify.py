r'''Negating yaw, pitch, and roll while retaining their original composition order gives the inverse rotation used to transform vector coordinates.'''

import json


def around_x(vector, direction):
    x, y, z = vector
    if direction == 0:
        return vector
    if direction == 1:
        return (x, -z, y)
    if direction == -1:
        return (x, z, -y)
    raise ValueError("unsupported turn")


def around_y(vector, direction):
    x, y, z = vector
    if direction == 0:
        return vector
    if direction == 1:
        return (z, y, -x)
    if direction == -1:
        return (-z, y, x)
    raise ValueError("unsupported turn")


def around_z(vector, direction):
    x, y, z = vector
    if direction == 0:
        return vector
    if direction == 1:
        return (-y, x, z)
    if direction == -1:
        return (y, -x, z)
    raise ValueError("unsupported turn")


def original(vector):
    return around_z(around_y(around_x(vector, 1), 1), 0)


def same_order_negation(vector):
    return around_z(around_y(around_x(vector, -1), -1), 0)


def reversed_order_inverse(vector):
    return around_x(around_y(around_z(vector, 0), -1), -1)


basis = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
for basis_vector in basis:
    assert reversed_order_inverse(original(basis_vector)) == basis_vector
    assert original(reversed_order_inverse(basis_vector)) == basis_vector

witness_vector = (1, 0, 0)
assert same_order_negation(witness_vector) == (0, 0, 1)
assert reversed_order_inverse(witness_vector) == (0, 1, 0)
assert same_order_negation(witness_vector) != reversed_order_inverse(witness_vector)

result = {
    "record_id": "reddit_askmath_14dg2d6",
    "verdict": "CONFIRMED",
    "notes": "Under the stated right-handed column-vector convention, exact recomputation shows that same-order angle negation is not the inverse because rotations do not generally commute. The refuted statement is substantive, not a typo.",
}
print(json.dumps(result, separators=(",", ":")))
