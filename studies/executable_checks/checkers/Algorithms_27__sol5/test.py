"""each Ai must contain exactly 3 non-zero elements"""

import json

semantic_instances = ()
for instance in semantic_instances:
    raise AssertionError("The supplied quote contains no semantic instances")

result = {
    "record_id": "Algorithms_27__sol5",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No witness can be formed from the supplied quote because it provides no concrete Ai or admissible domain.",
    "refutation_explanation": "The claim is not decidable from the supplied data: Ai, its elements, the meaning of containment, and the quantified collection are all unspecified.",
    "search_space": "Exhaustively swept the empty set of semantic instances supplied by the quote (0 instances); no candidate Ai is present to test."
}
print(json.dumps(result, separators=(",", ":")))
