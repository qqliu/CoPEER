r"""For the discrete-time kernel \(\cmss P(x,y)=C_{xy}/\pi(x)\), the generator \(\cmss L=\cmss P-\mathrm{id}\) equals the unnormalized conductance sum \(\sum_y C_{xy}[f(y)-f(x)]\)."""

import json
from fractions import Fraction

record_id = "arxiv_1412.0175v2__source_enriched_codex"
confirmed_notes = "Exact rational recomputation gives (P-id)f(0)=1 and the unnormalized conductance sum=2. The refuted statement is plainly a missing-normalization-factor typo: the sum requires division by pi(0)."


def conductance(x, y):
    if (x == 0 and y == 1) or (x == 1 and y == 0):
        return 2
    if x == y and x not in (0, 1):
        return 1
    return 0


def mass(x):
    return 2 if x in (0, 1) else 1


def neighbors(x):
    if x == 0:
        return (1,)
    if x == 1:
        return (0,)
    return (x,)


def transition(x, y):
    return Fraction(conductance(x, y), mass(x))


def value(x):
    return -1 if x == 0 else 0


representatives = (0, 1, -2, 3)
kernel_valid = all(
    sum((transition(x, y) for y in neighbors(x)), Fraction(0, 1))
    == Fraction(1, 1)
    for x in representatives
)
formula_valid = all(
    transition(x, y) == Fraction(conductance(x, y), mass(x))
    for x in representatives
    for y in neighbors(x)
)
symmetric = all(
    conductance(x, y) == conductance(y, x)
    for x in representatives
    for y in representatives
)

x = 0
normalized_generator = sum(
    (transition(x, y) * value(y) for y in neighbors(x)),
    Fraction(0, 1),
) - value(x)
unnormalized_sum = sum(
    (conductance(x, y) * (value(y) - value(x)) for y in neighbors(x)),
    0,
)

witness_established = (
    kernel_valid
    and formula_valid
    and symmetric
    and normalized_generator == Fraction(1, 1)
    and unnormalized_sum == 2
    and normalized_generator != unnormalized_sum
)

if witness_established:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The supplied witness did not pass exact independent validation."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}))
