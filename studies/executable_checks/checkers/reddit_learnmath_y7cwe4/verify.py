"""Every finite set equipped with an associative binary operation contains an idempotent element."""

import json

REPORT = {
    "record_id": "reddit_learnmath_y7cwe4",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms the literal claim fails: the empty finite carrier has the unique total binary operation, associativity holds vacuously, and no idempotent exists. This is plainly an omitted nonempty hypothesis rather than a substantive counterexample to the usual finite-semigroup theorem.",
}

carrier = ()
operation_graph = ()
required_inputs = tuple((left, right) for left in carrier for right in carrier)
actual_inputs = tuple(entry[0] for entry in operation_graph)

assert len(carrier) == 0
assert required_inputs == ()
assert actual_inputs == required_inputs
assert all(entry[1] in carrier for entry in operation_graph)
assert all(
    sum(1 for entry in operation_graph if entry[0] == pair) == 1
    for pair in required_inputs
)

associative = True
for first in carrier:
    for second in carrier:
        for third in carrier:
            left_middle = next(value for pair, value in operation_graph if pair == (first, second))
            right_middle = next(value for pair, value in operation_graph if pair == (second, third))
            left_value = next(value for pair, value in operation_graph if pair == (left_middle, third))
            right_value = next(value for pair, value in operation_graph if pair == (first, right_middle))
            if left_value != right_value:
                associative = False

has_idempotent = any(
    value == element
    for element in carrier
    for pair, value in operation_graph
    if pair == (element, element)
)

assert associative
assert not has_idempotent
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
