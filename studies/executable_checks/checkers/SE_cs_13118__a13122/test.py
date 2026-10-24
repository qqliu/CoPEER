r"""$$ \Delta(c^n) = (c-1)c^n, \quad \Sigma(c^n) = \frac{c^n-1}{c-1}.$$"""

import json
from fractions import Fraction

RECORD_ID = "SE_cs_13118__a13122"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness: the supplied quote does not define the operators or "
    "specify which values of c and n are admissible."
)
REFUTATION_EXPLANATION = (
    "The quote only states the displayed equations; it does not define Delta or "
    "Sigma, quantify c and n, specify their domains, or address c = 1. Thus the "
    "left-hand sides cannot be evaluated from the supplied data. The quotient on "
    "the displayed right-hand side is undefined at c = 1, but that is not "
    "honestly a counterexample without knowing that c = 1 is admissible and what "
    "the claimed equality means there."
)
SEARCH_SPACE = (
    "All 153 ordered integer pairs (c, n) with -8 <= c <= 8 and 0 <= n <= 8, "
    "visited in increasing c and then increasing n. The sweep exhaustively checks "
    "whether both displayed right-hand sides are arithmetically defined; it cannot "
    "evaluate the undefined operators Delta and Sigma."
)

checked = 0
undefined_quotients = []
for c in range(-8, 9):
    for n in range(0, 9):
        checked += 1
        delta_rhs = (c - 1) * (c ** n)
        numerator = c ** n - 1
        denominator = c - 1
        if denominator == 0:
            undefined_quotients.append((c, n))
        else:
            sigma_rhs = Fraction(numerator, denominator)
            assert delta_rhs == (c - 1) * (c ** n)
            assert sigma_rhs == Fraction(numerator, denominator)

assert checked == 153
assert undefined_quotients == [(1, n) for n in range(0, 9)]

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
