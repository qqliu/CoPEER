"""The asserted identity equating the constrained sum of monomials with the displayed product of finite sums."""

import itertools
import json
import math

VALUES = (0, 1, -1)
first_witness = None
case_count = 0

for a in (1, 2):
    for b in (1, 2):
        if b < a:
            continue
        for m in (1, 2, 3):
            coordinate_count = max(b, m)
            for coordinates in itertools.product(VALUES, repeat=coordinate_count):
                case_count += 1
                left = sum(
                    math.prod(coordinates[index - 1] for index in indices)
                    for indices in itertools.combinations_with_replacement(
                        range(a, b + 1), m
                    )
                )
                factor = sum(coordinates[j - 1] for j in range(1, m + 1))
                right = math.prod(factor for k in range(a, b + 1))
                if left != right and first_witness is None:
                    first_witness = (a, b, m, coordinates, left, right)

assert case_count == 129
assert first_witness == (1, 1, 2, (0, 1), 0, 1)

result = {
    "record_id": "proofwiki_70137__codex_expansion",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take a = b = 1, m = 2, x_1 = 0, and x_2 = 1.",
    "refutation_explanation": "The left side has only the tuple (j_1,j_2) = (1,1), so it equals x_1 x_1 = 0. The right side has one factor and equals x_1 + x_2 = 1. Thus the asserted equality gives 0 = 1.",
    "search_space": "All 129 cases with 1 <= a <= b <= 2, 1 <= m <= 3, and every needed coordinate x_1,...,x_max(b,m) independently in the fixed order (0, 1, -1); every case was evaluated exactly, and the first counterexample in that order is reported."
}
print(json.dumps(result, sort_keys=True))
