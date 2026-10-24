"""The goal is to disprove the existence of some $r'$, because that would show that incrementing the right pointer is not the correct way to reach the target sum."""

import json

CANDIDATES = ()

for candidate in CANDIDATES:
    raise AssertionError("The supplied quote defines no checkable candidates")

result = {
    "record_id": "SE_cs_169250__q",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No witness can be specified from the supplied quote.",
    "refutation_explanation": "The supplied quote does not define r', its domain, the underlying data, the pointer-update rule, the target sum, or the predicate whose existence is to be disproved. Therefore no candidate can be checked as a counterexample without inventing absent definitions.",
    "search_space": "The empty set of fully specified candidate witnesses, represented by the fixed tuple (); all 0 candidates are swept. This empty sweep is not evidence for or against the claim.",
}

print(json.dumps(result, separators=(",", ":")))
