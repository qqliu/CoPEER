"""For every ordered integral domain D, the map g: Z → D defined by g(n)=n·1_D is onto D."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_2305__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take D = Q with its usual order. The bounded sweep finds 1/2 in D, "
    "while every g(n) is the integer rational n/1."
)
REFUTATION_EXPLANATION = (
    "The exact rational 1/2 cannot equal g(n)=n·1_Q for any integer n, "
    "because every such image has reduced denominator 1 whereas 1/2 has "
    "reduced denominator 2. Thus g: Z → Q is not onto, and Q is an "
    "ordered integral domain."
)
SEARCH_SPACE = (
    "All 10 numerator-denominator pairs (p,q) with p visited in the fixed "
    "order (0,1,-1,2,-2) and q visited in the fixed order (1,2), "
    "interpreted exactly as Fraction(p,q); the entire bounded space is swept."
)

numerators = (0, 1, -1, 2, -2)
denominators = (1, 2)
violations = []

for q in denominators:
    for p in numerators:
        element = Fraction(p, q)
        if element.denominator != 1:
            violations.append(element)

assert violations
assert violations[0] == Fraction(1, 2)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
