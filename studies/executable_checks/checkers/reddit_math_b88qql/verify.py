r"""An exact finite presentation over one Noetherian subring passes to the ambient direct-limit ring as an exact presentation of the extended ideal."""

import json

MODULUS = 2


def ring_element(integer_coordinate, residue_coordinate):
    return (integer_coordinate, residue_coordinate % MODULUS)


def ring_add(left, right):
    return ring_element(left[0] + right[0], left[1] + right[1])


def ring_multiply(left, right):
    return ring_element(left[0] * right[0], left[1] * right[1])


def diagonal_embedding(integer):
    return ring_element(integer, integer)


def base_presentation_map(integer):
    return 2 * integer


def base_presentation_inverse(even_integer):
    assert even_integer % 2 == 0
    return even_integer // 2


def extended_presentation_map(element):
    return ring_multiply(diagonal_embedding(2), element)


def belongs_to_two_r(element):
    return element[0] % 2 == 0 and element[1] == 0


REPORT = {
    "record_id": "reddit_math_b88qql",
    "verdict": "CONFIRMED",
    "notes": "Exact integer arithmetic independently verifies the witness: A = Z maps diagonally into R = Z x (Z/2Z), A -> 2A by n |-> 2n is exact, but e = (0,1) is nonzero and multiplication by 2 sends both e and 0 to 0 in 2R. Thus the extended map is not injective. The refuted statement is substantive, not a typo.",
}

zero = ring_element(0, 0)
one = ring_element(1, 1)
assert diagonal_embedding(0) == zero
assert diagonal_embedding(1) == one
assert diagonal_embedding(-7 + 11) == ring_add(
    diagonal_embedding(-7), diagonal_embedding(11)
)
assert diagonal_embedding(-7 * 11) == ring_multiply(
    diagonal_embedding(-7), diagonal_embedding(11)
)

# The original A-module map n |-> 2n has the displayed exact inverse on 2A.
for source_integer in range(-32, 33):
    image_integer = base_presentation_map(source_integer)
    assert image_integer % 2 == 0
    assert base_presentation_inverse(image_integer) == source_integer
    if image_integer == 0:
        assert source_integer == 0
for target_integer in range(-64, 65, 2):
    assert base_presentation_map(base_presentation_inverse(target_integer)) == target_integer

# Multiplication by the embedded integer 2 maps R onto the ideal 2R.
for integer_coordinate in range(-16, 17):
    for residue_coordinate in range(MODULUS):
        source = ring_element(integer_coordinate, residue_coordinate)
        image = extended_presentation_map(source)
        assert image == ring_element(2 * integer_coordinate, 0)
        assert belongs_to_two_r(image)
for even_coordinate in range(-32, 33, 2):
    target = ring_element(even_coordinate, 0)
    preimage = ring_element(even_coordinate // 2, 0)
    assert extended_presentation_map(preimage) == target

# This exact concrete collision proves that the extended map is not injective.
e = ring_element(0, 1)
assert e != zero
assert extended_presentation_map(e) == zero
assert extended_presentation_map(e) == extended_presentation_map(zero)
assert belongs_to_two_r(zero)

print(json.dumps(REPORT, separators=(",", ":")))
