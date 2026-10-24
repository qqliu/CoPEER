r"""The axis Re(s) = 1/2 is the only axis on which zeros of the Riemann zeta function are possible."""

import json
from fractions import Fraction

# Compute coefficients through x^3 of x/(exp(x)-1) by exact formal
# power-series inversion. Its x^m coefficient is B_m/m!.
factorials = [1]
for index in range(1, 5):
    factorials.append(factorials[-1] * index)

denominator = []
for degree in range(4):
    denominator.append(Fraction(1, factorials[degree + 1]))

reciprocal = [Fraction(1, 1)]
for degree in range(1, 4):
    convolution = Fraction(0, 1)
    for offset in range(1, degree + 1):
        convolution += denominator[offset] * reciprocal[degree - offset]
    reciprocal.append(-convolution)

bernoulli_three = reciprocal[3] * factorials[3]
zeta_minus_two = bernoulli_three * Fraction(1, 3)
witness_real_part = Fraction(-2, 1)

assert denominator[0] == Fraction(1, 1)
assert bernoulli_three == Fraction(0, 1)
assert zeta_minus_two == Fraction(0, 1)
assert witness_real_part != Fraction(1, 2)

REPORT = {
    "record_id": "reddit_mathematics_1sl6haf",
    "verdict": "CONFIRMED",
    "notes": "An exact generating-series recomputation gives B_3 = 0 and hence zeta(-2) = 0, while Re(-2) is not 1/2. The refuted statement is substantive as written, though it likely omitted the crucial qualifier “nontrivial”; this is not merely a plain typo."
}

print(json.dumps(REPORT, separators=(",", ":"), ensure_ascii=False))
