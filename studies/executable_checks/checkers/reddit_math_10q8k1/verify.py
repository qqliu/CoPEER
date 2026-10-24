"""Any complex-valued function is constant."""

import json

REPORT = {
    "record_id": "reddit_math_10q8k1",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation verifies the stated witness: f(0)=0 and f(1)=1 defines a complex-valued function with unequal outputs. The refuted statement is substantive, not plainly a typo.",
}

# Represent each Gaussian integer a+bi exactly by the integer pair (a, b).
domain = (0, 1)
graph = ((0, (0, 0)), (1, (1, 0)))

assert tuple(argument for argument, value in graph) == domain
assert len({argument for argument, value in graph}) == len(domain)
assert all(
    isinstance(real, int) and isinstance(imaginary, int)
    for argument, (real, imaginary) in graph
)
outputs = tuple(value for argument, value in graph)
assert outputs[0] == (0, 0)
assert outputs[1] == (1, 0)
assert outputs[0] != outputs[1]
assert not all(value == outputs[0] for value in outputs)

print(json.dumps(REPORT, separators=(",", ":")))
