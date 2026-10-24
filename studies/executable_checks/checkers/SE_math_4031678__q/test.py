r"""$${100\choose 50}\cdot 1\leq 100\cdot {99\choose 49}\implies 51\leq 50,$$"""

import json
from math import comb

record_id = "SE_math_4031678__q"
witness_description = (
    "For the sole tuple (100, 50, 1, 100, 99, 49, 51, 50), the antecedent is "
    "100891344545564193334812497256 <= 5044567227278209666740624862800, "
    "while the consequent is 51 <= 50."
)
refutation_explanation = (
    "The antecedent is true and the consequent is false, so the displayed "
    "implication is false."
)
search_space = (
    "Exactly the singleton ordered space {(100, 50, 1, 100, 99, 49, 51, 50)} "
    "was swept; its fields are the two binomial arguments, the multiplier 1, "
    "the multiplier 100, the second binomial arguments, and the two consequent "
    "integers, in that order."
)

cases = ((100, 50, 1, 100, 99, 49, 51, 50),)
found = False
for n1, k1, factor1, factor2, n2, k2, consequent_left, consequent_right in cases:
    antecedent_left = comb(n1, k1) * factor1
    antecedent_right = factor2 * comb(n2, k2)
    antecedent = antecedent_left <= antecedent_right
    consequent = consequent_left <= consequent_right
    if antecedent and not consequent:
        found = True
        if antecedent_left != 100891344545564193334812497256:
            raise RuntimeError("unexpected first binomial value")
        if antecedent_right != 5044567227278209666740624862800:
            raise RuntimeError("unexpected right-hand value")

if not found:
    raise RuntimeError("the exhaustive singleton sweep did not find the witness")

result = {
    "record_id": record_id,
    "outcome": "WITNESS_FOUND",
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
