r"""$$\sum_{1\leq m^+ + m^- \leq 17}\binom{17}{m^+ + m^-}\binom{m^+ + m^-}{m^+}\left(\frac{1}{2^{m^+ + m^-}}\binom{m^+ + m^-}{m^+}\right)^{10} that is true by direct computation."""

import json
from fractions import Fraction
from math import comb


record_id = "mse_667257__ans672555"
outcome = "NO_WITNESS_INCONCLUSIVE"
witness_description = (
    "No counterexample is definable because the supplied text gives no equality, "
    "inequality, target value, or other predicate for the displayed sum."
)
refutation_explanation = (
    "The quote supplies only a summation expression followed by the words \"that is "
    "true by direct computation.\" A numerical expression alone is not a proposition, "
    "and the quote also does not explicitly define the domains of m^+ and m^-. The "
    "program therefore performs only an illustrative exact finite sweep and does not "
    "treat it as evidence for or against an unstated claim."
)
search_space = (
    "Illustrative exact sweep of all 170 ordered pairs (m^+, m^-) in "
    "{0,1,...,17}^2 satisfying 1 <= m^+ + m^- <= 17, evaluated in "
    "lexicographic loop order with Fraction arithmetic; this is not an exhaustive "
    "space for the underspecified claim."
)

# Evaluate every term under the explicitly bounded illustrative interpretation.
total = Fraction(0, 1)
pair_count = 0
for m_plus in range(18):
    for m_minus in range(18):
        k = m_plus + m_minus
        if 1 <= k <= 17:
            pair_count += 1
            multiplicity = comb(17, k) * comb(k, m_plus)
            factor = Fraction(comb(k, m_plus), 2 ** k)
            total += multiplicity * factor ** 10

if pair_count != 170:
    raise RuntimeError("finite sweep count mismatch")
if not isinstance(total, Fraction):
    raise RuntimeError("exact arithmetic invariant failed")

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
