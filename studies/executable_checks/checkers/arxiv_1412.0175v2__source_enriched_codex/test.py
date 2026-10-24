r"""For the discrete-time kernel \(\cmss P(x,y)=C_{xy}/\pi(x)\), the generator \(\cmss L=\cmss P-\mathrm{id}\) equals the unnormalized conductance sum \(\sum_y C_{xy}[f(y)-f(x)]\)."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1412.0175v2__source_enriched_codex"
WITNESS_DESCRIPTION = "On the integers, set C_01=C_10=2, pi(0)=pi(1)=2, and P(0,1)=P(1,0)=1. For every integer z outside {0,1}, set C_zz=pi(z)=1 and P(z,z)=1, with all other conductances zero. Let f(0)=-1 and f(z)=0 for z != 0. At x=0, (P-id)f(0)=1, while sum_y C_0y[f(y)-f(0)]=2."
REFUTATION_EXPLANATION = "At x=0 the normalized generator is (C_01/pi(0))*(f(1)-f(0))=(2/2)*1=1, whereas the claimed unnormalized expression is C_01*(f(1)-f(0))=2. Thus the equality fails for this valid discrete-time Markov kernel."
SEARCH_SPACE = "All 54 tuples (w,a,b,x) in {1,2,3} x {-1,0,1} x {-1,0,1} x {0,1}, in fixed nested-loop order. Each tuple denotes the integer-state kernel with C_01=C_10=w, pi(0)=pi(1)=w, isolated unit self-loops at every other integer, and the function f(0)=a, f(1)=b, f(z)=0 elsewhere. Every tuple was checked using Fraction arithmetic."

violations = []
for w in (1, 2, 3):
    conductance = ((0, w), (w, 0))
    pi = (w, w)
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            values = (a, b)
            for x in (0, 1):
                row_sum = sum(
                    (Fraction(conductance[x][y], pi[x]) for y in (0, 1)),
                    Fraction(0, 1),
                )
                assert row_sum == Fraction(1, 1)
                generator = sum(
                    (
                        Fraction(conductance[x][y], pi[x]) * values[y]
                        for y in (0, 1)
                    ),
                    Fraction(0, 1),
                ) - values[x]
                unnormalized = sum(
                    (
                        conductance[x][y] * (values[y] - values[x])
                        for y in (0, 1)
                    ),
                    0,
                )
                if generator != unnormalized:
                    violations.append((w, a, b, x, generator, unnormalized))

assert violations
assert violations[0] == (2, -1, 0, 0, Fraction(1, 1), 2)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False))
