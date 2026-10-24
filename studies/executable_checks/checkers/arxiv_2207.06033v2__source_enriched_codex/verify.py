r"""For every nonconstant polynomial F in \mathbb{Z}[x_1,\ldots,x_r] and every prime p, the number c_p(F) of zeros of F modulo p satisfies c_p(F) \leq \deg(F)p^{r-1}."""

import json

record_id = "arxiv_2207.06033v2__source_enriched_codex"
verdict = "CONFIRMED"
notes = (
    "The refuted statement is substantive, not plainly a typo: it omits a "
    "hypothesis ensuring that F remains nonzero modulo p. For F(x_1)=2x_1 "
    "and p=2, both residue classes are zeros, so c_2(F)=2>1."
)

p = 2
variables = 1
coefficients = (0, 2)

assert p > 1
assert all(p % divisor != 0 for divisor in range(2, p))
assert all(isinstance(coefficient, int) for coefficient in coefficients)
assert coefficients[-1] != 0

degree = len(coefficients) - 1
assert degree > 0

zero_count = 0
for residue in range(p):
    value = 0
    for exponent, coefficient in enumerate(coefficients):
        value += coefficient * (residue ** exponent)
    if value % p == 0:
        zero_count += 1

factor = 1
for _ in range(variables - 1):
    factor *= p
bound = degree * factor

assert zero_count == 2
assert bound == 1
assert zero_count > bound

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
