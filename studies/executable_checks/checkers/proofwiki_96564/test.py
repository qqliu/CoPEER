"""The proof claims that for arbitrary field F, a^2 + b^2 != 0 exactly when (a,b) != (0,0), hence every nonzero element of E = F x F has a multiplicative inverse (a/(a^2+b^2), -b/(a^2+b^2)), and correspondingly (line 0128) that a c - b d = 0 and a d + b c = 0 with (c,d) != (0,0) forces a = b = 0. Both steps, and hence the main claim that E is always a field, fail whenever -1 is a square in F."""

import itertools
import json

P = 5

pair_hits = []
for a, b in itertools.product(range(P), repeat=2):
    if (a, b) != (0, 0) and (a * a + b * b) % P == 0:
        pair_hits.append((a, b))

product_hits = []
for a, b, c, d in itertools.product(range(P), repeat=4):
    if ((a, b) != (0, 0) and
            (c, d) != (0, 0) and
            (a * c - b * d) % P == 0 and
            (a * d + b * c) % P == 0):
        product_hits.append((a, b, c, d))

assert pair_hits[0] == (1, 2)
assert product_hits[0] == (1, 2, 1, 3)

result = {
    "record_id": "proofwiki_96564",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take F=Z/5Z. Since 2^2=4=-1 modulo 5, (a,b)=(1,2) is nonzero and a^2+b^2=1+4=0. With (c,d)=(1,3), also nonzero, ac-bd=1-6=0 and ad+bc=3+2=0 modulo 5.",
    "refutation_explanation": "This contradicts both asserted steps: a nonzero pair has a^2+b^2=0, and the nonzero pair (c,d)=(1,3) satisfies ac-bd=ad+bc=0 without a=b=0. Thus E has two nonzero elements whose product is zero, so E is not a field; the proposed inverse also has zero denominator.",
    "search_space": "Over F=Z/5Z, the program exhaustively sweeps all 25 ordered pairs (a,b) in F^2 and all 625 ordered quadruples (a,b,c,d) in F^4, in lexicographic order, testing the stated expressions modulo 5."
}

print(json.dumps(result, separators=(",", ":")))
