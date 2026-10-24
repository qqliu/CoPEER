"""For arbitrary real numbers x_1,…,x_n, if their sum is n, then their product is at most 1."""

import itertools
import json

coordinate_values = range(-1, 6)
first_witness = None
tested = 0

for n in range(1, 4):
    for values in itertools.product(coordinate_values, repeat=n):
        tested += 1
        if sum(values) != n:
            continue
        product = 1
        for value in values:
            product *= value
        if product > 1 and first_witness is None:
            first_witness = (n, values, product)

assert tested == 399
assert first_witness == (3, (-1, -1, 5), 5)

result = {
    "record_id": "reddit_learnmath_9m5f5w",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n=3 with (x_1,x_2,x_3)=(-1,-1,5): the sum is 3 and the product is 5.",
    "refutation_explanation": "The tuple consists of real numbers because integers are real, satisfies (-1)+(-1)+5=3=n, but has product (-1)(-1)(5)=5>1.",
    "search_space": "Exhaustive sweep of all 399 pairs (n, tuple), where n is in {1,2,3} and the tuple has length n with every coordinate in {-1,0,1,2,3,4,5}; every tuple was checked, and tuples whose sum equals n were tested for product greater than 1."
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
