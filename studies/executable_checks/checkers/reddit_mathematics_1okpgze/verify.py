r"""The proof claims that -log² N + log N - 3 is positive for every N > e⁴."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_mathematics_1okpgze",
    "verdict": "CONFIRMED",
    "notes": "For the exact symbolic witness N=e^5, monotonicity of the exponential gives N>e^4, while log N=5 and therefore -(log N)^2+log N-3=-23≤0. The refuted statement is substantive, not plainly a typo.",
}

# Represent e^k by its integer exponent. The exponential function is strictly
# increasing because e>1. The first two exact terms of e's positive series
# already give the lower bound e >= 1 + 1 > 1.
e_series_lower_bound = Fraction(1, 1) + Fraction(1, 1)
assert e_series_lower_bound > Fraction(1, 1)

witness_exponent = 5
threshold_exponent = 4
assert witness_exponent > threshold_exponent

# For N=e^5, the exact inverse identity log(e^k)=k gives log N=5.
log_n = Fraction(witness_exponent, 1)
expression = -(log_n ** 2) + log_n - Fraction(3, 1)
assert expression == Fraction(-23, 1)
assert expression <= Fraction(0, 1)

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
