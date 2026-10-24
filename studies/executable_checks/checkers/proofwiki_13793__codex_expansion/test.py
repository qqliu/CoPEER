"""The substitution sec(theta)=x/|a| is valid and domain-preserving under the stated hypotheses without requiring a≠0."""

import itertools
import json


values = (-1, 0, 1)
invalid_pairs = []

for a, x in itertools.product(values, values):
    if abs(a) == 0:
        invalid_pairs.append((a, x))

witness_a, witness_x = invalid_pairs[0]

result = {
    "record_id": "proofwiki_13793__codex_expansion",
    "outcome": "WITNESS_FOUND",
    "witness_description": (
        f"a={witness_a} and x={witness_x} (indeed, any x in the swept set): "
        "|a|=0, so the right-hand side x/|a| is undefined."
    ),
    "refutation_explanation": (
        "At a=0, |a|=0, so x/|a| has zero denominator and is undefined. "
        "Therefore the displayed substitution is not valid at a=0; a nonzero "
        "condition (or some hypothesis implying it) is necessary."
    ),
    "search_space": (
        "All 9 ordered integer pairs (a, x) in (-1, 0, 1) × (-1, 0, 1), "
        "traversed in itertools.product order; each pair was checked exactly "
        "for |a|=0."
    ),
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
