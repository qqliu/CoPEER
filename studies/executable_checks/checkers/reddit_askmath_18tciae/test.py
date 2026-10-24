"""For arbitrary fixed positive ε and δ, one can choose a satisfying ε ≤ a < δ."""

import json
from itertools import product

values = (1, 2, 3)
counterexamples = []

for epsilon, delta in product(values, repeat=2):
    if epsilon >= delta:
        counterexamples.append((epsilon, delta))

if counterexamples[0] != (1, 1):
    raise RuntimeError("deterministic search invariant failed")

result = {
    "record_id": "reddit_askmath_18tciae",
    "outcome": "WITNESS_FOUND",
    "witness_description": "ε = 1 and δ = 1 are fixed positive values for which no a satisfies ε ≤ a < δ.",
    "refutation_explanation": "Substitution gives 1 ≤ a < 1. The first inequality requires a ≥ 1, while the second requires a < 1, so they cannot both hold. Thus the universal claim fails.",
    "search_space": "All 9 ordered pairs (ε, δ) in {1, 2, 3} × {1, 2, 3}, in itertools.product order, were swept exactly; a pair was classified as a counterexample exactly when ε ≥ δ, because ε ≤ a < δ would then imply ε < δ."
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
