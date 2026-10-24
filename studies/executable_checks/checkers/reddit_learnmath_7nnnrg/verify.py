r"""For any partitions of X and Y, the intersection of all sets Ai × Bj is empty."""

import json


def is_partition(universe, blocks):
    if not blocks or any(not block for block in blocks):
        return False
    accumulated = set()
    for block in blocks:
        if accumulated.intersection(block):
            return False
        accumulated.update(block)
    return accumulated == universe


def cartesian_product(left, right):
    return {(x, y) for x in left for y in right}


x_set = {0}
y_set = {0}
a_blocks = ({0},)
b_blocks = ({0},)

assert is_partition(x_set, a_blocks)
assert is_partition(y_set, b_blocks)

products = [
    cartesian_product(a_block, b_block)
    for a_block in a_blocks
    for b_block in b_blocks
]
assert products

common = set(products[0])
for product_set in products[1:]:
    common.intersection_update(product_set)

assert common == {(0, 0)}
assert common

result = {
    "record_id": "reddit_learnmath_7nnnrg",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms that the singleton partitions have one block product, {(0, 0)}, whose full intersection is nonempty. The refuted statement is substantive as written, not plainly a typo.",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
