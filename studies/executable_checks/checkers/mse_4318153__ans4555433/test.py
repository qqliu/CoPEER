r"""If $a_n$ is a sequence satisfying a linear recurrence then $\limsup_{n \to \infty} \sqrt[n]{|a_n|} = r$ exists and is equal to the absolute value of the largest root of the characteristic polynomial of the recurrence. The above argument (suitably tightened up) shows that $\lim_{n \to \infty} \sqrt[n]{v_n} = 1$, so the roots of the characteristic polynomial have absolute value $\le 1$."""

import itertools
import json

RECORD_ID = "mse_4318153__ans4555433"
VALUES = tuple(range(-2, 3))


def is_counterexample(r, s, q):
    if q == 0 or (q != r and q != s):
        return False
    recurrence_coefficient_1 = r + s
    recurrence_coefficient_2 = -(r * s)
    recurrence_holds_for_all_n = (
        q * q
        == recurrence_coefficient_1 * q + recurrence_coefficient_2
    )
    sequence_growth = abs(q)
    largest_root_modulus = max(abs(r), abs(s))
    return recurrence_holds_for_all_n and sequence_growth < largest_root_modulus


hits = []
for roots_and_base in itertools.product(VALUES, repeat=3):
    if is_counterexample(*roots_and_base):
        hits.append(roots_and_base)

assert hits
assert hits[0] == (-2, -1, -1)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": "For n≥0, take a_n=(-1)^n and the order-two recurrence a_n=-3a_{n-1}-2a_{n-2} for n≥2.",
    "refutation_explanation": "The recurrence has characteristic polynomial x^2+3x+2=(x+2)(x+1), whose largest root modulus is 2. Yet |a_n|=1 for every n, so sqrt[n]{|a_n|}=1 for every n≥1 and the limsup is 1, not 2.",
    "search_space": "All 125 ordered triples (r,s,q) in {-2,-1,0,1,2}^3 were evaluated in lexicographic order. For each nonzero q equal to r or s, the program exactly checks the sequence a_n=q^n against the recurrence with characteristic polynomial (x-r)(x-s), and compares |q| with max(|r|,|s|).",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
