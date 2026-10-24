"""The logarithmic argument proves the power rule for every real exponent a at every non-negative real x."""

import json

RECORD_ID = "reddit_learnmath_2dto7y"
EXPONENTS = (1,)
BASES = (0,)

witness = None
for a in EXPONENTS:
    for x in BASES:
        logarithm_is_really_defined = x > 0
        if not logarithm_is_really_defined:
            witness = (a, x)
            break
    if witness is not None:
        break

if witness == (1, 0):
    outcome = "WITNESS_FOUND"
    witness_description = "a=1 and x=0."
    refutation_explanation = (
        "The claimed logarithmic argument requires the real natural logarithm at x, "
        "but ln(0) is undefined. Thus the argument cannot apply at the non-negative "
        "real input x=0, contradicting the assertion that it proves the rule at every "
        "non-negative x."
    )
else:
    outcome = "NO_WITNESS_EXHAUSTIVE"
    witness_description = "No witness was found."
    refutation_explanation = "The bounded search found no input where the logarithmic step is undefined."

search_space = (
    "The singleton Cartesian product a in {1}, x in {0}; exactly one pair was checked "
    "in fixed tuple order."
)

result = {
    "record_id": RECORD_ID,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
