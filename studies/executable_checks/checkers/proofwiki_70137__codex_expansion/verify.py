r"""The asserted identity equating the constrained sum of monomials with the displayed product of finite sums."""

import json


def nondecreasing_indices(lower, upper, remaining):
    if remaining == 0:
        yield ()
        return
    for first in range(lower, upper + 1):
        for rest in nondecreasing_indices(first, upper, remaining - 1):
            yield (first,) + rest


def integer_product(values):
    result = 1
    for value in values:
        result *= value
    return result


a = 1
b = 1
m = 2
x = {1: 0, 2: 1}

left = 0
for indices in nondecreasing_indices(a, b, m):
    left += integer_product(x[index] for index in indices)

right = 1
for k in range(a, b + 1):
    factor = 0
    for j in range(1, m + 1):
        factor += x[j]
    right *= factor

assert left == 0
assert right == 1
assert left != right

result = {
    "record_id": "proofwiki_70137__codex_expansion",
    "verdict": "CONFIRMED",
    "notes": "Exact integer recomputation gives left side 0 and right side 1 for the reported witness. The displayed statement is plainly a typo or malformed transcription: the product index k is unused in its factor.",
}
print(json.dumps(result, separators=(",", ":")))
