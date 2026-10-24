"""Then the single point {x} is itself a face of P: it is the intersection of P with the supporting hyperplane aT k z = bk that touches P at x."""

import json

REPORT = {
    "record_id": "Algorithms_47__sol4",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No witness: the permitted quote contains no fully specified mathematical instance to test.",
    "refutation_explanation": "No refutation is claimed. The sentence starts with \"Then\" but supplies no antecedent and does not specify P, x, aT k, bk, the ambient dimension, or the meaning of \"touches.\" Its truth therefore cannot be evaluated from the permitted data alone.",
    "search_space": "The exact bounded space was the tuple of fully specified mathematical instances supplied by the permitted quote. Its cardinality is 0, so all 0 entries were swept; this empty illustrative sweep is not exhaustive evidence for the claim.",
}

EXPLICIT_INSTANCES = ()
examined = 0
first_witness = None

for description, is_counterexample in EXPLICIT_INSTANCES:
    examined += 1
    if is_counterexample:
        first_witness = description
        break

if first_witness is not None:
    derived_outcome = "WITNESS_FOUND"
elif examined == 0:
    derived_outcome = "NO_WITNESS_INCONCLUSIVE"
else:
    derived_outcome = "NO_WITNESS_EXHAUSTIVE"

assert examined == len(EXPLICIT_INSTANCES)
assert derived_outcome == REPORT["outcome"]
assert tuple(REPORT) == (
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
)

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
