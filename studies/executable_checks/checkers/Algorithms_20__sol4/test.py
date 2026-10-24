r"""Now let emin be an edge of PT(s, t) whose weight is m (such an edge exists by definition of m)."""

import json

REPORT = {
    "record_id": "Algorithms_20__sol4",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness is claimed: the quote supplies no definition of PT(s, t), no edge set, no weight function, and no definition or value of m.",
    "refutation_explanation": "Whether an edge of weight m exists depends on the missing definitions and data. Supplying an interpretation of PT(s, t), its edges, its weights, or m would invent information absent from the quote, so the claim cannot be evaluated.",
    "search_space": "Exhaustively swept the empty tuple of concrete edge-and-weight instances supplied by the quote (0 instances); the quote specifies no checkable mathematical instance.",
}

SOURCE_QUOTE = "Now let emin be an edge of PT(s, t) whose weight is m (such an edge exists by definition of m)."
PROVIDED_CONCRETE_INSTANCES = ()
MISSING_DATA = (
    "definition of PT(s, t)",
    "edge set",
    "weight function",
    "definition or value of m",
)

checked = 0
for _instance in PROVIDED_CONCRETE_INSTANCES:
    checked += 1

if MISSING_DATA:
    derived_outcome = "NO_WITNESS_INCONCLUSIVE"
elif checked == len(PROVIDED_CONCRETE_INSTANCES):
    derived_outcome = "NO_WITNESS_EXHAUSTIVE"
else:
    raise AssertionError("bounded sweep did not complete")

assert SOURCE_QUOTE == "Now let emin be an edge of PT(s, t) whose weight is m (such an edge exists by definition of m)."
assert checked == len(PROVIDED_CONCRETE_INSTANCES)
assert len(PROVIDED_CONCRETE_INSTANCES) == 0
assert derived_outcome == REPORT["outcome"]
assert tuple(REPORT) == (
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
)
print(json.dumps(REPORT, separators=(",", ":")))
