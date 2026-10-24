"""In the stated toy model, the cutoff γ_k, distributed as the maximum of c independent Uniform[0,1] variables, has expectation 1−1/c."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_2110.07024v2__source_enriched_codex"
C_VALUES = tuple(range(2, 9))
mismatches = []

for c in C_VALUES:
    actual_expectation = Fraction(c, c + 1)
    claimed_expectation = Fraction(c - 1, c)
    if actual_expectation != claimed_expectation:
        mismatches.append(
            (c, actual_expectation, claimed_expectation,
             actual_expectation - claimed_expectation)
        )

first = mismatches[0]
assert first == (2, Fraction(2, 3), Fraction(1, 2), Fraction(1, 6))

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": (
        "c=2: the supplied CDF is F(x)=x^2, so the maximum has exact "
        "expectation 2/3; the claimed formula gives 1/2."
    ),
    "refutation_explanation": (
        "For c=2, E[γ_k]=∫_0^1(1−x^2) dx=2/3, whereas 1−1/c=1/2; "
        "the nonzero difference is 1/6, so this instance violates the "
        "claimed formula."
    ),
    "search_space": (
        "All integer values c in {2,3,4,5,6,7,8}; for each, the exact "
        "expectation c/(c+1) implied by F(x)=x^c was compared with 1−1/c."
    ),
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
