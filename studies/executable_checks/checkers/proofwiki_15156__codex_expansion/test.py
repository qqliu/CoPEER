"""In the stated zero-exponent case, the function φ(x)=x^(q/p) is well-defined as a real function and can be used in Jensen's inequality."""

import json
from fractions import Fraction

record_id = "proofwiki_15156__codex_expansion"
outcome = "NO_WITNESS_INCONCLUSIVE"
witness_description = "No certified witness: the supplied data do not specify whether p or q is the zero exponent, their allowed values, or how 0^0 is interpreted."
refutation_explanation = "The finite sweep exposes two possible obstructions: p=0 makes q/p undefined, while q=0 with x=0 and p≠0 reaches the convention-sensitive expression 0^0. The quote does not establish which parameter case is intended or provide an exponentiation convention, so neither obstruction can honestly be certified as belonging to the stated case."
search_space = "All 75 triples (x,p,q) in {0,1,2}×{-2,-1,0,1,2}×{-2,-1,0,1,2} were swept in lexicographic order; 15 have p=0, and 4 have x=0, q=0, p≠0."

xs = tuple(range(3))
ps = tuple(range(-2, 3))
qs = tuple(range(-2, 3))
examined = []
denominator_zero = []
zero_to_zero = []

for x in xs:
    for p in ps:
        for q in qs:
            candidate = (x, p, q)
            examined.append(candidate)
            if p == 0:
                denominator_zero.append(candidate)
            else:
                exponent = Fraction(q, p)
                if x == 0 and exponent == 0:
                    zero_to_zero.append(candidate)

assert len(examined) == 75
assert len(denominator_zero) == 15
assert len(zero_to_zero) == 4

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, ensure_ascii=False))
