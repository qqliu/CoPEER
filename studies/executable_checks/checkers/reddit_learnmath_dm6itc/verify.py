r"""The asserted identity f(x) = f(-x) + (-f(x)) holds for an arbitrary function on a domain closed under negation."""

import json

REPORT = {
    "record_id": "reddit_learnmath_dm6itc",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not plainly a typo. For D={0} and f(0)=1, the domain is closed under negation, while the identity has left side 1 and right side 0.",
}


domain = frozenset((0,))
function_table = {0: 1}

assert set(function_table) == set(domain)
assert all((-argument) in domain for argument in domain)

witness = 0
left_side = function_table[witness]
right_side = function_table[-witness] + (-function_table[witness])

assert left_side == 1
assert right_side == 0
assert left_side != right_side
assert tuple(REPORT) == ("record_id", "verdict", "notes")

print(json.dumps(REPORT, separators=(",", ":")))
