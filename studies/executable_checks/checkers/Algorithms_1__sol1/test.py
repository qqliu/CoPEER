r"""noting that Pr[X <=(1 -eps)pN] = Pr[N -X >=(1 +eps)(1 -p)N] and applying the upper-tail bound to N -X (N, 1 -p)."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "Algorithms_1__sol1",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No claim-level witness is justified: the quote specifies neither the probability law of X nor admissible domains for N, p, and eps.",
    "refutation_explanation": "At N=1, p=1/4, eps=1/2 on support {0,1}, the left event is {X=0} and the right event is empty. Thus the identity is false under P(X=0)=1 but true under P(X=1)=1. Since the quote does not define the intended law or say which laws are admissible, this finite diagnostic cannot decide the target claim.",
    "search_space": "Exhaustively checked the singleton parameter triple N=1, p=1/4, eps=1/2, outcomes X in {0,1}, and the two exact point-mass laws P(X=0)=1 and P(X=1)=1, in that order. This is only a diagnostic finite space because the quote supplies no admissible domain.",
}

parameter_space = ((1, Fraction(1, 4), Fraction(1, 2)),)
law_space = (
    (Fraction(1, 1), Fraction(0, 1)),
    (Fraction(0, 1), Fraction(1, 1)),
)
observations = []

for N, p, eps in parameter_space:
    support = tuple(range(N + 1))
    left_cutoff = (Fraction(1, 1) - eps) * p * N
    right_cutoff = (Fraction(1, 1) + eps) * (Fraction(1, 1) - p) * N
    for weights in law_space:
        assert len(weights) == len(support)
        assert all(weight >= 0 for weight in weights)
        assert sum(weights, Fraction(0, 1)) == Fraction(1, 1)
        left_probability = sum(
            (weights[x] for x in support if Fraction(x, 1) <= left_cutoff),
            Fraction(0, 1),
        )
        right_probability = sum(
            (
                weights[x]
                for x in support
                if Fraction(N - x, 1) >= right_cutoff
            ),
            Fraction(0, 1),
        )
        observations.append((weights, left_probability, right_probability))

unequal_cases = [item for item in observations if item[1] != item[2]]
equal_cases = [item for item in observations if item[1] == item[2]]
assert unequal_cases == [
    (law_space[0], Fraction(1, 1), Fraction(0, 1))
]
assert equal_cases == [
    (law_space[1], Fraction(0, 1), Fraction(0, 1))
]

print(json.dumps(REPORT, separators=(",", ":")))
