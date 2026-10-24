"""However, adding e back connects these components because e connects A to B (by definition of A and B)."""

import json

RECORD_ID = "Algorithms_36__sol5"
TARGET_CLAIM = "However, adding e back connects these components because e connects A to B (by definition of A and B)."
SOURCE_QUOTE = "However, adding e back connects these components because e connects A to B (by definition of A and B)."

WITNESS_DESCRIPTION = (
    "No concrete witness can be named because the supplied data contains no graph, "
    "edge incidence, components, or definitions of A and B."
)
REFUTATION_EXPLANATION = (
    "The source quote exactly repeats the target claim and supplies no mathematical "
    "instance or definitions against which connectivity can be checked. The available "
    "concrete-instance space is empty, so the finite sweep cannot establish or refute "
    "the claim."
)
SEARCH_SPACE = (
    "Exactly one textual item was inspected: the ordered pair consisting of the "
    "supplied target claim and the supplied source quote. It contains zero concrete "
    "mathematical instances; the resulting concrete-instance search space was the "
    "empty tuple."
)

textual_space = ((TARGET_CLAIM, SOURCE_QUOTE),)
inspected = 0
for claim, quote in textual_space:
    inspected += 1
    assert claim == quote
assert inspected == 1

concrete_instances = ()
found_witness = False
for _instance in concrete_instances:
    found_witness = True
assert not found_witness

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
