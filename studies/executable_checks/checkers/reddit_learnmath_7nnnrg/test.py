"""For any partitions of X and Y, the intersection of all sets Ai × Bj is empty."""

import itertools
import json


def set_partitions(n):
    """Return every partition of range(n) once, in fixed order."""
    result = []
    for labels in itertools.product(range(n), repeat=n):
        if labels[0] != 0:
            continue
        valid = True
        largest = 0
        for index in range(1, n):
            if labels[index] > largest + 1:
                valid = False
                break
            if labels[index] > largest:
                largest = labels[index]
        if not valid:
            continue
        blocks = tuple(
            frozenset(element for element in range(n) if labels[element] == label)
            for label in range(largest + 1)
        )
        result.append(blocks)
    return tuple(result)


first_witness = None
swept = 0

for m in range(1, 5):
    partitions_x = set_partitions(m)
    for n in range(1, 5):
        partitions_y = set_partitions(n)
        for partition_x in partitions_x:
            for partition_y in partitions_y:
                swept += 1
                block_products = tuple(
                    frozenset(itertools.product(block_x, block_y))
                    for block_x in partition_x
                    for block_y in partition_y
                )
                common = set(block_products[0])
                for block_product in block_products[1:]:
                    common.intersection_update(block_product)
                if common and first_witness is None:
                    first_witness = (
                        m,
                        n,
                        partition_x,
                        partition_y,
                        frozenset(common),
                    )

assert swept == 529
assert first_witness == (
    1,
    1,
    (frozenset({0}),),
    (frozenset({0}),),
    frozenset({(0, 0)}),
)

result = {
    "record_id": "reddit_learnmath_7nnnrg",
    "outcome": "WITNESS_FOUND",
    "witness_description": "X={0}, Y={0}, with partitions A={{0}} and B={{0}}; the sole block product is {(0,0)}, so its intersection is {(0,0)}.",
    "refutation_explanation": "The claimed intersection is not empty for the displayed partitions: (0,0) belongs to every Ai × Bj (there is exactly one such product). Thus this single instance falsifies the universal claim.",
    "search_space": "All 529 ordered pairs of set partitions (A,B) of X_m={0,1,...,m-1} and Y_n={0,1,...,n-1}, for every m,n in {1,2,3,4}; every block product Ai × Bj was formed and their full intersection tested.",
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
