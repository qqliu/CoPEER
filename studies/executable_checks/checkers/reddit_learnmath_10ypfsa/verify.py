r"""The initialization a_1=0 implies the strict inequality a_2>a_1 and hence begins a strictly increasing sequence."""

import json
from fractions import Fraction

record_id = "reddit_learnmath_10ypfsa"
confirmed_notes = (
    "Exact recomputation gives a_2=a_1=0 for the reported witness, so the "
    "strict inequality fails. The refuted statement is substantive, not "
    "plainly a typo: strictness requires an additional nondegeneracy condition "
    "such as positive probability that X>0."
)
invalid_notes = "The reported witness does not establish failure of the strict inequality."

support = (0,)
probabilities = (Fraction(1, 1),)
r = 0
a_1 = Fraction(0, 1)

total_probability = sum(probabilities, Fraction(0, 1))
valid_distribution = (
    total_probability == Fraction(1, 1)
    and all(probability >= Fraction(0, 1) for probability in probabilities)
    and all(value == 0 for value in support)
)
denominator = 1 + r
valid_recurrence = denominator != 0
expected_max = sum(
    (
        probability * (value if value >= a_1 else a_1)
        for value, probability in zip(support, probabilities)
    ),
    Fraction(0, 1),
)
a_2 = expected_max * Fraction(1, denominator)
refutes_strictness = valid_distribution and valid_recurrence and not (a_2 > a_1)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if refutes_strictness else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if refutes_strictness else invalid_notes,
}
print(json.dumps(result))
