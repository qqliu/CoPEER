"""The proof claims that X ∉ A ∩ B implies X ∈ A △ B."""

import itertools
import json

RECORD_ID = "reddit_learnmath_918alc"
WITNESS_DESCRIPTION = "Let the universe be {X}, with A = ∅ and B = ∅."
REFUTATION_EXPLANATION = (
    "X ∉ A ∩ B is true because A ∩ B = ∅, but X ∈ A △ B is false "
    "because A △ B = ∅. Thus the implication fails."
)
SEARCH_SPACE = (
    "All 4 ordered pairs (A, B) of subsets of the singleton universe {X}, "
    "enumerated by the two exact membership bits (X ∈ A, X ∈ B) in "
    "itertools.product((False, True), repeat=2)."
)

witness_found = False
for in_a, in_b in itertools.product((False, True), repeat=2):
    antecedent = not (in_a and in_b)
    in_symmetric_difference = in_a != in_b
    if antecedent and not in_symmetric_difference:
        if not in_a and not in_b:
            witness_found = True
            break

if witness_found:
    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
else:
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
