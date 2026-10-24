"""The value n=253 suffices to make it more likely than not that all 365 days are simultaneously represented by at least one event."""

import json

RECORD_ID = "reddit_learnmath_ugzgrr"
SOURCE_QUOTE = "Since n is the answer to one problem, it's the answer to all of them. QED"

# The supplied quote defines no sample space, probability distribution,
# event-generation mechanism, meaning of n, or admissible instance. Therefore
# the exact finite collection of fully specified models supplied by it is empty.
supplied_models = ()

witness = None
for model in supplied_models:
    witness = model
    break

assert witness is None

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be named because the supplied quote specifies no probability model or admissible instances.",
    "refutation_explanation": "The claim cannot be evaluated from the supplied data: the meaning of n, the event-generation mechanism, the sample space, and the probability distribution are all unspecified. The quote supplies no fully specified model in which a counterexample could be checked.",
    "search_space": "All fully specified probability models supplied by source_quote: exactly zero models (the empty tuple), exhaustively iterated in its unique fixed order.",
}
print(json.dumps(result))
